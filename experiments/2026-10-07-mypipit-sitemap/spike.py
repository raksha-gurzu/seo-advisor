"""Spike: what does the MyPipit sitemap contain? Throwaway code; never import it.

Safety code copied from ~/projects/Gurzu/SEOAdvisor/src/seo_engine/providers/base.py and
fetcher.py (robots_body). Run: see README.md. Read-only, 1 request per second.
"""

import collections
import ipaddress
import socket
import sys
import time
import zlib
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import httpcore
import httpx
from lxml import etree
from protego import Protego

SITE = "https://marketplace.mypipit.com"
UA = "seo-advisor-research/0.1 (Gurzu SEO audit; read-only)"
DELAY_S = 1.0
MAX_FILES = 60
OUT = Path(__file__).parent / "fixtures"


# --- copied guard (SEOAdvisor base.py) ---
def ip_is_public(address: str) -> bool:
    ip = ipaddress.ip_address(address.split("%", 1)[0])
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ip = ip.ipv4_mapped
    return ip.is_global and not ip.is_multicast


def public_addresses(host: str, port: int | None = None) -> list[str]:
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except (OSError, UnicodeError):
        return []
    addresses = list(dict.fromkeys(info[4][0] for info in infos))
    return addresses if addresses and all(ip_is_public(a) for a in addresses) else []


def guard_request(request: httpx.Request) -> None:
    host = request.url.host
    if not host or not public_addresses(host):
        raise httpx.TransportError(f"blocked: {host} is not a public address", request=request)


class PublicOnlyBackend(httpcore.SyncBackend):
    def connect_tcp(self, host: str, port: int, timeout: float | None = None,
                    local_address: str | None = None, socket_options: Any = None) -> httpcore.NetworkStream:
        addresses = public_addresses(host, port)
        if not addresses:
            raise httpcore.ConnectError(f"blocked: {host} is not a public address")
        return super().connect_tcp(addresses[0], port, timeout, local_address, socket_options)


def public_client(**kwargs: Any) -> httpx.Client:
    transport = httpx.HTTPTransport(retries=0)
    pool = transport._pool
    if not hasattr(pool, "_network_backend"):
        raise RuntimeError("httpx/httpcore changed: cannot install PublicOnlyBackend")
    pool._network_backend = PublicOnlyBackend()
    return httpx.Client(transport=transport, event_hooks={"request": [guard_request]}, **kwargs)


def bounded_get(client: httpx.Client, url: str, max_bytes: int, deadline_s: float) -> tuple[int, bytes, str, bool]:
    started = time.monotonic()
    with client.stream("GET", url) as resp:
        size, chunks = 0, []
        for chunk in resp.iter_bytes():
            size += len(chunk)
            if size > max_bytes:
                return resp.status_code, b"", resp.headers.get("content-type", ""), True
            if time.monotonic() - started > deadline_s:
                raise httpx.ReadTimeout("deadline", request=resp.request)
            chunks.append(chunk)
        return resp.status_code, b"".join(chunks), resp.headers.get("content-type", ""), False


def gunzip_capped(data: bytes, max_bytes: int) -> bytes:
    unpacker = zlib.decompressobj(16 + zlib.MAX_WBITS)
    out = unpacker.decompress(data, max_bytes + 1)
    if len(out) > max_bytes or unpacker.unconsumed_tail:
        raise ValueError("gzip too large")
    return out


def parse_sitemap(content: bytes) -> tuple[str, list[tuple[str, str]], str]:
    """(kind, [(loc, lastmod)], error). recover=False: broken XML is reported, not hidden."""
    if content[:2] == b"\x1f\x8b":
        content = gunzip_capped(content, 50_000_000)
    parser = etree.XMLParser(resolve_entities=False, no_network=True, recover=False, huge_tree=False)
    try:
        root = etree.fromstring(content, parser)
    except etree.XMLSyntaxError as exc:
        return "invalid", [], str(exc)
    kind = etree.QName(root).localname
    child = {"urlset": "url", "sitemapindex": "sitemap"}.get(kind)
    if child is None:
        return "invalid", [], f"root element is {kind}"
    entries = []
    for node in root.xpath(f"./*[local-name()='{child}']"):
        loc = "".join(node.xpath("./*[local-name()='loc']/text()")).strip()
        lastmod = "".join(node.xpath("./*[local-name()='lastmod']/text()")).strip()
        if loc:
            entries.append((loc, lastmod))
    return kind, entries, ""


def save(url: str, content: bytes) -> str:
    name = urlparse(url).path.strip("/").replace("/", "_") or "root"
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_bytes(content)
    return name


def main() -> int:
    host = urlparse(SITE).hostname or ""
    print(f"host {host} public addresses: {public_addresses(host)}")
    client = public_client(follow_redirects=True, timeout=20, headers={"User-Agent": UA})
    requests = 0

    def get(url: str, max_bytes: int) -> tuple[int, bytes, str, bool]:
        nonlocal requests
        if requests:
            time.sleep(DELAY_S)
        requests += 1
        return bounded_get(client, url, max_bytes, 60)

    status, body, ctype, too_large = get(urljoin(SITE, "/robots.txt"), 512_000)
    print(f"robots.txt: HTTP {status}, {len(body)} bytes, {ctype}, too_large={too_large}")
    save("/robots.txt", body)
    robots = Protego.parse(body.decode("utf-8", "replace") if status < 400 else "")
    sitemaps = list(robots.sitemaps) or [urljoin(SITE, "/sitemap.xml")]
    print(f"sitemaps listed in robots.txt: {list(robots.sitemaps)}")

    queue, seen, pages = list(sitemaps), set(), []
    while queue and len(seen) < MAX_FILES:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        if not robots.can_fetch(url, UA):
            print(f"  SKIP (robots disallow) {url}")
            continue
        status, body, ctype, too_large = get(url, 50_000_000)
        name = save(url, body)
        kind, entries, error = parse_sitemap(body) if status == 200 and not too_large else ("http", [], f"HTTP {status}")
        print(f"  {url} -> HTTP {status}, {len(body)} bytes, {kind}, {len(entries)} entries {error} [saved {name}]")
        if kind == "sitemapindex":
            queue += [loc for loc, _ in entries]
        elif kind == "urlset":
            pages += entries
    client.close()

    urls = [loc for loc, _ in pages]
    unique = list(dict.fromkeys(urls))
    print(f"\nrequests: {requests}, sitemap files read: {len(seen)}")
    print(f"page URLs: {len(urls)}, unique: {len(unique)}")
    hosts = collections.Counter(urlparse(u).netloc for u in unique)
    print(f"hosts: {dict(hosts)}")
    print(f"with query string: {sum(1 for u in unique if urlparse(u).query)}")
    first = collections.Counter((urlparse(u).path.strip('/').split('/') or [''])[0] for u in unique)
    print(f"first path segment (top 20): {first.most_common(20)}")
    depth = collections.Counter(len([p for p in urlparse(u).path.split('/') if p]) for u in unique)
    print(f"path depth: {sorted(depth.items())}")
    lastmods = [lm for _, lm in pages]
    print(f"lastmod present: {sum(1 for lm in lastmods if lm)}/{len(lastmods)}, distinct values: {len(set(lastmods))}")
    print("examples:")
    for seg, _ in first.most_common(8):
        sample = next(u for u in unique if (urlparse(u).path.strip('/').split('/') or [''])[0] == seg)
        print(f"  [{seg}] {sample}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

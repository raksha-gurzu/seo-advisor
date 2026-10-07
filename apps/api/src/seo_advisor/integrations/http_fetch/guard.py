"""SSRF guard: reach only public web addresses; connect to the checked address."""

import ipaddress
import socket
import time
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any
from urllib.parse import urlparse

import httpcore
import httpx

ALLOWED_SCHEMES = frozenset({"http", "https"})
ALLOWED_PORTS = frozenset({80, 443})
DEFAULT_PORTS = {"http": 80, "https": 443}

# IPv6 forms that carry an IPv4 address or are not public (RFC 6052, 6145, 4291, 3879).
_NAT64 = ipaddress.IPv6Network("64:ff9b::/96")
_IPV4_TRANSLATED = ipaddress.IPv6Network("::ffff:0:0:0/96")
_NOT_PUBLIC_V6 = (
    ipaddress.IPv6Network("::/96"),  # IPv4-compatible (deprecated), also :: and ::1
    ipaddress.IPv6Network("64:ff9b:1::/48"),  # local-use NAT64
    ipaddress.IPv6Network("fec0::/10"),  # site-local (deprecated)
)


class BlockedAddressError(httpx.TransportError):
    """A request to a non-public address, port or scheme was stopped before sending."""


def ip_is_public(address: str) -> bool:
    """Only globally routable unicast addresses.

    `is_global` also rejects ranges that `is_private` misses, for example 100.64.0.0/10.
    An IPv6 address that carries an IPv4 address (::ffff:a.b.c.d, NAT64,
    IPv4-translated) is judged by its IPv4 part.
    """
    ip: ipaddress.IPv4Address | ipaddress.IPv6Address
    ip = ipaddress.ip_address(address.split("%", 1)[0])
    if isinstance(ip, ipaddress.IPv6Address):
        if ip.ipv4_mapped:
            ip = ip.ipv4_mapped
        elif ip in _NAT64 or ip in _IPV4_TRANSLATED:
            ip = ipaddress.IPv4Address(int(ip) & 0xFFFF_FFFF)
        elif any(ip in network for network in _NOT_PUBLIC_V6):
            return False
    return ip.is_global and not ip.is_multicast


def public_addresses(host: str, port: int | None = None) -> list[str]:
    """The host's addresses, or [] if it does not resolve or ANY address is not public.

    Never cached: a cached "public" answer would let the name later point somewhere
    else (DNS rebinding). Known limit: the system resolver sets the lookup timeout.
    """
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except OSError, UnicodeError:
        # Not resolvable means not reachable: the caller blocks the request.
        return []
    addresses = list(dict.fromkeys(str(info[4][0]) for info in infos))
    return addresses if addresses and all(ip_is_public(a) for a in addresses) else []


def is_public_url(url: str) -> bool:
    """True only for http(s) on port 80 or 443, to a host with public addresses only."""
    parts = urlparse(url)
    host = parts.hostname
    if parts.scheme not in ALLOWED_SCHEMES or not host:
        return False
    try:
        port = parts.port or DEFAULT_PORTS[parts.scheme]
    except ValueError:
        # urlparse rejects a port that is not a number from 0 to 65535: not a web URL.
        return False
    if port not in ALLOWED_PORTS:
        return False
    return bool(public_addresses(host.lower()))


def require_web_scheme(url: str) -> None:
    """Raise BlockedAddressError for a scheme other than http or https."""
    scheme = urlparse(url).scheme
    if scheme not in ALLOWED_SCHEMES:
        raise BlockedAddressError(
            f"blocked: scheme {scheme!r} is not allowed "
            "(only http/https, port 80 or 443, public addresses)"
        )


def guard_request(request: httpx.Request) -> None:
    """httpx request hook. It runs before every request that the client sends."""
    if not is_public_url(str(request.url)):
        raise BlockedAddressError(
            f"blocked: {request.url.host} is not allowed "
            "(only http/https, port 80 or 443, public addresses)",
            request=request,
        )


# --- Total time limit for one request -------------------------------------------------

_deadline: ContextVar[float | None] = ContextVar("http_fetch_deadline", default=None)


@contextmanager
def deadline_scope(deadline: float) -> Iterator[float]:
    """Inside this block, every network read and write ends by `deadline`.

    An inner scope can only make the deadline earlier, never later. The block gets
    the deadline in force.
    """
    current = _deadline.get()
    effective = deadline if current is None else min(current, deadline)
    token = _deadline.set(effective)
    try:
        yield effective
    finally:
        _deadline.reset(token)


def capped_timeout(
    timeout: float | None, error: type[httpcore.TimeoutException]
) -> float | None:
    """The timeout, but not more than the time left. Raise `error` if none is left."""
    deadline = _deadline.get()
    if deadline is None:
        return timeout
    left = deadline - time.monotonic()
    if left <= 0:
        raise error("total time limit reached")
    return left if timeout is None else min(timeout, left)


class DeadlineStream(httpcore.NetworkStream):
    """A network stream whose reads and writes obey the total time limit.

    httpx timeouts apply to each read, so a server that sends one header byte just
    before each timeout could hold a request open for days.
    """

    def __init__(self, inner: httpcore.NetworkStream) -> None:
        self._inner = inner

    def read(self, max_bytes: int, timeout: float | None = None) -> bytes:
        return self._inner.read(
            max_bytes, capped_timeout(timeout, httpcore.ReadTimeout)
        )

    def write(self, buffer: bytes, timeout: float | None = None) -> None:
        self._inner.write(buffer, capped_timeout(timeout, httpcore.WriteTimeout))

    def close(self) -> None:
        self._inner.close()

    def start_tls(
        self,
        ssl_context: Any,
        server_hostname: str | None = None,
        timeout: float | None = None,
    ) -> httpcore.NetworkStream:
        timeout = capped_timeout(timeout, httpcore.ConnectTimeout)
        return DeadlineStream(
            self._inner.start_tls(ssl_context, server_hostname, timeout)
        )

    def get_extra_info(self, info: str) -> Any:
        return self._inner.get_extra_info(info)


class PublicOnlyBackend(httpcore.SyncBackend):
    """Resolve the host once, require public addresses, connect to the checked address.

    Without this, the check and the connection would each look up the name. A hostile
    DNS server could answer "public" first and "10.0.0.5" second. TLS still uses the
    host name (SNI), and the Host header does not change.
    """

    def connect_tcp(
        self,
        host: str,
        port: int,
        timeout: float | None = None,
        local_address: str | None = None,
        socket_options: Any = None,
    ) -> httpcore.NetworkStream:
        addresses = public_addresses(host, port)
        if not addresses:
            # Not an httpcore error, so httpx passes it through unchanged.
            raise BlockedAddressError(f"blocked: {host} is not a public address")
        timeout = capped_timeout(timeout, httpcore.ConnectTimeout)
        stream = super().connect_tcp(
            addresses[0], port, timeout, local_address, socket_options
        )
        return DeadlineStream(stream)

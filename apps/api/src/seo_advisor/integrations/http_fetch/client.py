"""The guarded HTTP client, download limits and the rate limit for each host."""

import threading
import time
import zlib
from collections.abc import Callable
from typing import NamedTuple

import httpx
from pydantic import BaseModel, ConfigDict

from seo_advisor.integrations.http_fetch.guard import (
    PublicOnlyBackend,
    deadline_scope,
    guard_request,
)


class FetchConfig(BaseModel):
    """Values come from Settings. No defaults here: thresholds are configuration."""

    model_config = ConfigDict(frozen=True)

    user_agent: str
    robots_agent: str
    timeout_s: float
    deadline_s: float
    min_delay_s: float


def public_client(
    config: FetchConfig, transport: httpx.BaseTransport | None = None
) -> httpx.Client:
    """An httpx client that can reach only public web addresses.

    `guard_request` checks every request. The real transport also connects only to the
    checked address (`PublicOnlyBackend`). Tests pass a fake `transport`; the guard hook
    stays on. httpx does not follow redirects: SafeFetcher checks each hop itself.
    """
    if transport is None:
        real = httpx.HTTPTransport(retries=0)
        pool = real._pool  # httpx has no public way to set the network backend
        if not hasattr(pool, "_network_backend"):
            raise RuntimeError(
                "httpx/httpcore changed: cannot install PublicOnlyBackend"
            )
        pool._network_backend = PublicOnlyBackend()
        transport = real
    return httpx.Client(
        transport=transport,
        event_hooks={"request": [guard_request]},
        follow_redirects=False,
        timeout=config.timeout_s,
        headers={"User-Agent": config.user_agent, "Accept-Encoding": "gzip"},
    )


class ContentEncodingError(ValueError):
    """The body uses an encoding that we do not accept, or the gzip data is broken."""


class Download(NamedTuple):
    url: str
    status: int
    content: bytes
    content_type: str
    too_large: bool
    location: str | None  # the redirect target; the redirect body is never read


class _Decoder:
    """Unpack a Content-Encoding with an output limit. Only identity and gzip.

    httpx's own decoder has no output limit, and it accepts stacked encodings
    ("gzip, gzip"): 173 bytes on the wire can become gigabytes in memory.
    """

    def __init__(self, encoding: str) -> None:
        names = [name.strip().lower() for name in encoding.split(",") if name.strip()]
        self._gzip: zlib._Decompress | None
        if names in ([], ["identity"]):
            self._gzip = None
        elif names in (["gzip"], ["x-gzip"]):
            self._gzip = zlib.decompressobj(16 + zlib.MAX_WBITS)
        else:
            raise ContentEncodingError(f"unsupported Content-Encoding: {encoding!r}")

    def feed(self, data: bytes, room: int) -> tuple[bytes, bool]:
        """(unpacked bytes, more than `room` bytes would come out)."""
        if self._gzip is None:
            return data, len(data) > room
        if self._gzip.eof:
            raise ContentEncodingError("data after the gzip data")
        try:
            out = self._gzip.decompress(data, room + 1)
        except zlib.error as exc:
            raise ContentEncodingError(f"invalid gzip body: {exc}") from None
        return out, len(out) > room or bool(self._gzip.unconsumed_tail)

    def finish(self) -> None:
        if self._gzip is None:
            return
        if not self._gzip.eof:
            raise ContentEncodingError("the gzip body ends early")
        if self._gzip.unused_data:
            raise ContentEncodingError("data after the gzip data")


def bounded_get(
    client: httpx.Client,
    url: str,
    max_bytes: int,
    deadline_s: float,
    *,
    keep_head: bool = False,
) -> Download:
    """One GET with a size limit and a total time limit. Redirects are not followed.

    The limit counts raw and unpacked bytes. If the body is too large, the result has
    `too_large=True` and no content, or the first `max_bytes` if `keep_head` is set.
    The total time limit covers connect, TLS, headers and body.
    """
    if max_bytes < 1:
        raise ValueError(f"max_bytes must be 1 or more, not {max_bytes}")
    with (
        deadline_scope(time.monotonic() + deadline_s) as deadline,
        client.stream("GET", url) as resp,
    ):
        content_type = resp.headers.get("content-type", "")
        if resp.is_redirect:
            location = resp.headers["location"]
            return Download(url, resp.status_code, b"", content_type, False, location)
        decoder = _Decoder(resp.headers.get("content-encoding", ""))
        raw_size, parts, size = 0, [], 0
        for chunk in resp.iter_raw():
            raw_size += len(chunk)
            out, over = decoder.feed(chunk, max_bytes - size)
            parts.append(out)
            size += len(out)
            if over or raw_size > max_bytes:
                head = b"".join(parts)[:max_bytes] if keep_head else b""
                return Download(url, resp.status_code, head, content_type, True, None)
            if time.monotonic() > deadline:
                raise httpx.ReadTimeout(
                    f"download took over {deadline_s:.0f} s", request=resp.request
                )
        decoder.finish()
        return Download(
            url, resp.status_code, b"".join(parts), content_type, False, None
        )


class TooLargeError(ValueError):
    """Unpacked data is larger than its limit."""


def gunzip_capped(data: bytes, max_bytes: int) -> bytes:
    """gzip.decompress with an output limit: 190 KB can unpack to 200 MB (gzip bomb)."""
    unpacker = zlib.decompressobj(16 + zlib.MAX_WBITS)
    try:
        out = unpacker.decompress(data, max_bytes + 1)
    except zlib.error as exc:
        raise ValueError(f"not valid gzip: {exc}") from None
    if len(out) > max_bytes or unpacker.unconsumed_tail:
        raise TooLargeError(f"unpacks to more than {max_bytes} bytes")
    return out


class HostRateLimiter:
    """At least `min_interval_s` between two requests to the same host. Thread-safe.

    Each call reserves the next free time slot for its host, then sleeps until then.
    """

    def __init__(
        self,
        min_interval_s: float,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._min_interval_s = min_interval_s
        self._clock = clock
        self._sleep = sleep
        self._next_free: dict[str, float] = {}
        self._lock = threading.Lock()

    def wait(self, host: str) -> None:
        with self._lock:
            now = self._clock()
            start = max(now, self._next_free.get(host, now))
            self._next_free[host] = start + self._min_interval_s
        if start > now:
            self._sleep(start - now)

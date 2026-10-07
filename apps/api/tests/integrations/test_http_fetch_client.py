import gzip
from collections.abc import Callable, Iterator

import httpx
import pytest

from seo_advisor.integrations.http_fetch.client import (
    ContentEncodingError,
    HostRateLimiter,
    TooLargeError,
    bounded_get,
    gunzip_capped,
)

Handler = Callable[[httpx.Request], httpx.Response]


def mock_client(handler: Handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


def answer(body: bytes, **headers: str) -> Handler:
    """Stream the body like a real server: httpx pre-reads a plain bytes body."""
    return lambda request: httpx.Response(200, content=iter([body]), headers=headers)


@pytest.mark.unit
def test_bounded_get_stops_at_the_size_limit() -> None:
    body = b"x" * 5000
    with mock_client(answer(body)) as client:
        too_big = bounded_get(
            client, "https://s.example/", max_bytes=1000, deadline_s=60
        )
        fits = bounded_get(
            client, "https://s.example/", max_bytes=10_000, deadline_s=60
        )
    assert too_big.too_large
    assert too_big.content == b""
    assert not fits.too_large
    assert fits.content == body
    assert fits.status == 200


@pytest.mark.unit
def test_bounded_get_can_keep_the_first_part() -> None:
    with mock_client(answer(b"x" * 5000)) as client:
        got = bounded_get(
            client, "https://s.example/", max_bytes=1000, deadline_s=60, keep_head=True
        )
    assert got.too_large
    assert got.content == b"x" * 1000


@pytest.mark.unit
def test_bounded_get_has_a_total_time_limit() -> None:
    with mock_client(answer(b"x")) as client, pytest.raises(httpx.ReadTimeout):
        bounded_get(client, "https://s.example/", max_bytes=10, deadline_s=-1)


@pytest.mark.unit
def test_a_gzip_body_is_unpacked() -> None:
    body = gzip.compress(b"<urlset/>")
    with mock_client(answer(body, **{"Content-Encoding": "gzip"})) as client:
        got = bounded_get(client, "https://s.example/", max_bytes=1000, deadline_s=60)
    assert got.content == b"<urlset/>"


@pytest.mark.unit
def test_a_gzip_bomb_body_stops_at_the_limit_of_the_unpacked_size() -> None:
    bomb = gzip.compress(b"\0" * 20_000_000)  # about 20 KB that unpacks to 20 MB
    with mock_client(answer(bomb, **{"Content-Encoding": "gzip"})) as client:
        got = bounded_get(
            client, "https://s.example/", max_bytes=1_000_000, deadline_s=60
        )
    assert got.too_large
    assert got.content == b""


@pytest.mark.unit
@pytest.mark.parametrize("encoding", ["gzip, gzip", "br", "zstd", "deflate, gzip"])
def test_stacked_and_unknown_encodings_are_refused(encoding: str) -> None:
    body = gzip.compress(gzip.compress(b"\0" * 1000))
    with (
        mock_client(answer(body, **{"Content-Encoding": encoding})) as client,
        pytest.raises(ContentEncodingError, match="unsupported Content-Encoding"),
    ):
        bounded_get(client, "https://s.example/", max_bytes=1000, deadline_s=60)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("body", "message"),
    [
        (b"not gzip at all", "invalid gzip"),
        (gzip.compress(b"hello world")[:-6], "ends early"),
        (gzip.compress(b"a") + b"extra", "after the gzip data"),
    ],
)
def test_broken_gzip_bodies_are_errors(body: bytes, message: str) -> None:
    with (
        mock_client(answer(body, **{"Content-Encoding": "gzip"})) as client,
        pytest.raises(ContentEncodingError, match=message),
    ):
        bounded_get(client, "https://s.example/", max_bytes=1000, deadline_s=60)


@pytest.mark.unit
def test_a_redirect_body_is_never_read() -> None:
    read: list[int] = []

    def endless() -> Iterator[bytes]:
        while True:
            read.append(1)
            yield b"x" * 65536

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers={"Location": "/next"}, content=endless())

    with mock_client(handler) as client:
        got = bounded_get(client, "https://s.example/a", max_bytes=1000, deadline_s=60)
    assert got.status == 302
    assert got.location == "/next"
    assert got.content == b""
    assert len(read) <= 1


@pytest.mark.unit
def test_gunzip_is_limited_against_gzip_bombs() -> None:
    bomb = gzip.compress(b"\0" * 1_000_000)  # about 1 KB that unpacks to 1 MB
    assert len(bomb) < 5_000
    with pytest.raises(TooLargeError):
        gunzip_capped(bomb, max_bytes=100_000)
    assert gunzip_capped(gzip.compress(b"hello"), max_bytes=100) == b"hello"
    with pytest.raises(ValueError, match="not valid gzip"):
        gunzip_capped(b"\x1f\x8bnot gzip", max_bytes=100)


class FakeTime:
    def __init__(self) -> None:
        self.now = 100.0
        self.sleeps: list[float] = []

    def clock(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


@pytest.mark.unit
def test_rate_limiter_waits_between_requests_to_the_same_host() -> None:
    t = FakeTime()
    limiter = HostRateLimiter(min_interval_s=1.0, clock=t.clock, sleep=t.sleep)
    limiter.wait("a.example")
    limiter.wait("a.example")
    t.now += 5.0  # a long pause: no wait is necessary
    limiter.wait("a.example")
    assert t.sleeps == [1.0]


@pytest.mark.unit
def test_rate_limiter_does_not_wait_between_different_hosts() -> None:
    t = FakeTime()
    limiter = HostRateLimiter(min_interval_s=1.0, clock=t.clock, sleep=t.sleep)
    limiter.wait("a.example")
    limiter.wait("b.example")
    assert t.sleeps == []


@pytest.mark.unit
@pytest.mark.parametrize("max_bytes", [0, -1])
def test_a_size_limit_below_one_byte_is_refused(max_bytes: int) -> None:
    with (
        mock_client(answer(b"x")) as client,
        pytest.raises(ValueError, match="max_bytes"),
    ):
        bounded_get(client, "https://s.example/", max_bytes=max_bytes, deadline_s=60)

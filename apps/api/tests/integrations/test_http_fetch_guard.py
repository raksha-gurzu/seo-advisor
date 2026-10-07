import socket
import time
from typing import Any

import httpcore
import pytest

from seo_advisor.integrations.http_fetch.client import FetchConfig, public_client
from seo_advisor.integrations.http_fetch.guard import (
    BlockedAddressError,
    DeadlineStream,
    PublicOnlyBackend,
    capped_timeout,
    deadline_scope,
    guard_request,
    ip_is_public,
    is_public_url,
    public_addresses,
)

PUBLIC_IP = "93.184.215.14"


@pytest.mark.unit
@pytest.mark.parametrize(
    ("address", "public"),
    [
        (PUBLIC_IP, True),
        ("2606:4700::6810:84e5", True),
        ("127.0.0.1", False),
        ("0.0.0.0", False),  # noqa: S104 - an address under test, nothing binds to it
        ("10.0.0.5", False),
        ("172.16.0.1", False),
        ("192.168.1.1", False),
        ("169.254.169.254", False),  # cloud metadata
        ("100.100.100.200", False),  # carrier-grade NAT; is_private misses it
        ("224.0.0.1", False),  # multicast
        ("198.18.0.1", False),  # benchmarking range
        ("::1", False),
        ("fc00::1", False),  # unique local
        ("fe80::1%eth0", False),  # link-local with a zone id
        ("fec0::1", False),  # deprecated site-local
        ("::ffff:127.0.0.1", False),  # IPv4-mapped loopback
        ("::ffff:93.184.215.14", True),
        ("::ffff:0:a00:5", False),  # IPv4-translated 10.0.0.5
        ("::7f00:1", False),  # IPv4-compatible 127.0.0.1 (deprecated form)
        ("64:ff9b::7f00:1", False),  # NAT64 form of 127.0.0.1
        ("64:ff9b::a9fe:a9fe", False),  # NAT64 form of 169.254.169.254
        ("64:ff9b::5db8:d70e", True),  # NAT64 form of a public address
        ("64:ff9b:1::1", False),  # local-use NAT64
    ],
)
def test_ip_is_public(address: str, public: bool) -> None:
    assert ip_is_public(address) is public


@pytest.mark.unit
@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:8000/",
        "http://10.0.0.5/",
        "http://169.254.169.254/latest/meta-data/",
        "http://[::1]/",
        "http://unknown.example/",
        "https://site.example:8443/",  # only ports 80 and 443
        "https://site.example:99999/",  # not a valid port
        "not a url",
        "ftp://site.example/file",
        "file:///etc/passwd",
    ],
)
def test_private_unknown_non_web_urls_are_not_public(
    dns: dict[str, list[str]], url: str
) -> None:
    dns["site.example"] = [PUBLIC_IP]
    assert not is_public_url(url)


@pytest.mark.unit
@pytest.mark.parametrize(
    "url",
    [
        "https://site.example/sitemap.xml",
        "https://site.example:443/",
        "http://site.example:80/",
        "http://site.example/",
    ],
)
def test_public_web_urls_are_public(dns: dict[str, list[str]], url: str) -> None:
    dns["site.example"] = [PUBLIC_IP]
    assert is_public_url(url)


@pytest.mark.unit
def test_one_private_address_makes_the_host_private(dns: dict[str, list[str]]) -> None:
    dns["mixed.example"] = [PUBLIC_IP, "10.0.0.5"]
    assert public_addresses("mixed.example") == []


@pytest.mark.unit
def test_dns_answers_are_not_cached(dns: dict[str, list[str]]) -> None:
    assert public_addresses("later.example") == []
    dns["later.example"] = [PUBLIC_IP]
    assert public_addresses("later.example") == [PUBLIC_IP]


@pytest.mark.unit
def test_backend_blocks_a_host_that_now_points_to_a_private_address(
    dns: dict[str, list[str]],
) -> None:
    dns["rebind.example"] = ["127.0.0.1"]
    with pytest.raises(BlockedAddressError, match="not a public address"):
        PublicOnlyBackend().connect_tcp("rebind.example", 80)


@pytest.mark.unit
def test_backend_connects_to_the_checked_address_and_wraps_the_stream(
    dns: dict[str, list[str]], monkeypatch: pytest.MonkeyPatch
) -> None:
    dns["site.example"] = [PUBLIC_IP]
    dialed: list[str] = []

    def connect_tcp(
        self: object, host: str, port: int, *args: Any, **kwargs: Any
    ) -> object:
        dialed.append(host)
        return object()

    monkeypatch.setattr(httpcore.SyncBackend, "connect_tcp", connect_tcp)
    stream = PublicOnlyBackend().connect_tcp("site.example", 443)
    assert dialed == [PUBLIC_IP]  # the checked IP, not a second lookup of the name
    assert isinstance(stream, DeadlineStream)


@pytest.mark.unit
def test_dns_rebinding_through_the_real_client_is_a_clear_block(
    config: FetchConfig, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The hook sees a public answer and the backend a private one: a clear block."""
    answers = iter([[PUBLIC_IP], ["127.0.0.1"]])

    def getaddrinfo(
        host: str, port: int | None, *args: Any, **kwargs: Any
    ) -> list[Any]:
        return [(0, 0, 0, "", (a, port or 0)) for a in next(answers)]

    monkeypatch.setattr(socket, "getaddrinfo", getaddrinfo)
    with pytest.raises(BlockedAddressError), public_client(config) as client:
        client.get("http://rebind.example/")


@pytest.mark.unit
def test_public_client_installs_the_guard_and_the_pinned_backend(
    config: FetchConfig,
) -> None:
    """Fails if an httpx or httpcore update removes the private hook of the guard."""
    with public_client(config) as client:
        assert guard_request in client.event_hooks["request"]
        assert client.follow_redirects is False  # SafeFetcher follows redirects itself
        pool = client._transport._pool  # type: ignore[attr-defined]  # private httpx API
        assert isinstance(pool._network_backend, PublicOnlyBackend)


@pytest.mark.unit
def test_a_request_to_a_private_address_is_never_sent(config: FetchConfig) -> None:
    with pytest.raises(BlockedAddressError), public_client(config) as client:
        client.get("http://127.0.0.1:80/")


@pytest.mark.unit
def test_capped_timeout_never_exceeds_the_time_left() -> None:
    with deadline_scope(time.monotonic() + 2.0):
        capped = capped_timeout(10.0, httpcore.ReadTimeout)
        unset = capped_timeout(None, httpcore.ReadTimeout)
        assert capped is not None
        assert capped <= 2.0
        assert unset is not None
        assert unset <= 2.0
        assert capped_timeout(0.5, httpcore.ReadTimeout) == 0.5
    assert capped_timeout(10.0, httpcore.ReadTimeout) == 10.0  # no scope, no change


@pytest.mark.unit
def test_capped_timeout_stops_when_the_time_is_over() -> None:
    with (
        deadline_scope(time.monotonic() - 1.0),
        pytest.raises(httpcore.ReadTimeout, match="total time limit"),
    ):
        capped_timeout(10.0, httpcore.ReadTimeout)


class FakeStream(httpcore.NetworkStream):
    def __init__(self) -> None:
        self.read_timeouts: list[float | None] = []

    def read(self, max_bytes: int, timeout: float | None = None) -> bytes:
        self.read_timeouts.append(timeout)
        return b"x"


@pytest.mark.unit
def test_deadline_stream_gives_each_read_only_the_time_left() -> None:
    inner = FakeStream()
    stream = DeadlineStream(inner)
    with deadline_scope(time.monotonic() + 1.0):
        stream.read(10, timeout=60.0)
    timeout = inner.read_timeouts[0]
    assert timeout is not None
    assert timeout <= 1.0


@pytest.mark.unit
def test_an_inner_deadline_scope_never_extends_the_outer_one() -> None:
    soon = time.monotonic() + 1.0
    with deadline_scope(soon) as outer, deadline_scope(soon + 100.0) as inner:
        assert outer == soon
        assert inner == soon
    with deadline_scope(soon) as outer, deadline_scope(soon - 0.5) as inner:
        assert inner == soon - 0.5

from collections.abc import Callable, Iterator
from contextlib import contextmanager

import httpx
import pytest

from seo_advisor.integrations.http_fetch import client as client_module
from seo_advisor.integrations.http_fetch.client import FetchConfig, HostRateLimiter
from seo_advisor.integrations.http_fetch.guard import (
    BlockedAddressError,
    guard_request,
)
from seo_advisor.integrations.http_fetch.guard import (
    deadline_scope as guard_deadline_scope,
)
from seo_advisor.integrations.http_fetch.robots import (
    DISALLOW_ALL,
    MAX_REDIRECTS,
    ROBOTS_MAX_BYTES,
    RedirectLimitError,
    RobotsDisallowedError,
    SafeFetcher,
    robots_body,
)

PUBLIC_IP = "93.184.215.14"
Handler = Callable[[httpx.Request], httpx.Response]
Page = tuple[int, bytes, dict[str, str]]


class RecordingLimiter(HostRateLimiter):
    def __init__(self) -> None:
        super().__init__(min_interval_s=0.0)
        self.hosts: list[str] = []

    def wait(self, host: str) -> None:
        self.hosts.append(host)


class Site:
    """A fake web: maps 'host/path' to a response, and records each request sent."""

    def __init__(self, dns: dict[str, list[str]], pages: dict[str, Page]) -> None:
        self.pages = pages
        self.sent: list[str] = []
        for key in pages:
            dns.setdefault(key.split("/", 1)[0], [PUBLIC_IP])

    def __call__(self, request: httpx.Request) -> httpx.Response:
        key = f"{request.url.host}{request.url.path}"
        self.sent.append(key)
        status, body, headers = self.pages.get(key, (404, b"", {}))
        # A fresh response that streams its body, like a real server.
        return httpx.Response(status, content=iter([body]), headers=headers)


def make(config: FetchConfig, site: Handler) -> tuple[SafeFetcher, RecordingLimiter]:
    limiter = RecordingLimiter()
    return SafeFetcher(
        config, transport=httpx.MockTransport(site), limiter=limiter
    ), limiter


def robots(text: str, status: int = 200) -> Page:
    return status, text.encode(), {}


def page(text: str) -> Page:
    return 200, text.encode(), {}


def redirect(location: str) -> Page:
    return 301, b"", {"Location": location}


@pytest.mark.unit
@pytest.mark.parametrize(
    ("status", "rules", "unreachable"),
    [
        (200, "User-agent: *\nDisallow: /x", False),
        (404, "", False),  # RFC 9309: no file, no rules
        (410, "", False),
        (304, DISALLOW_ALL, True),  # a final 3xx with no target: treat as unreachable
        (401, DISALLOW_ALL, False),  # stricter than the RFC, on purpose
        (403, DISALLOW_ALL, False),
        (429, DISALLOW_ALL, True),
        (503, DISALLOW_ALL, True),  # RFC 9309: unreachable, disallow everything
        (None, DISALLOW_ALL, True),
    ],
)
def test_robots_body_follows_rfc_9309(
    status: int | None, rules: str, unreachable: bool
) -> None:
    assert robots_body(status, "User-agent: *\nDisallow: /x") == (rules, unreachable)


@pytest.mark.unit
def test_a_disallowed_url_is_never_requested(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    site = Site(
        dns, {"s.example/robots.txt": robots("User-agent: *\nDisallow: /private")}
    )
    safe, _ = make(config, site)
    with pytest.raises(RobotsDisallowedError, match=r"disallowed by robots\.txt"):
        safe.get("https://s.example/private/page", max_bytes=1000)
    assert site.sent == ["s.example/robots.txt"]


@pytest.mark.unit
def test_an_allowed_url_is_fetched_and_rate_limited(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    site = Site(
        dns,
        {
            "s.example/robots.txt": robots("User-agent: *\nDisallow: /private"),
            "s.example/sitemap.xml": page("page"),
        },
    )
    safe, limiter = make(config, site)
    got = safe.get("https://s.example/sitemap.xml", max_bytes=1000)
    assert got.status == 200
    assert got.content == b"page"
    assert got.url == "https://s.example/sitemap.xml"
    assert limiter.hosts == ["s.example", "s.example"]  # robots.txt waits too


@pytest.mark.unit
def test_a_redirect_to_a_disallowed_path_is_never_requested(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    site = Site(
        dns,
        {
            "s.example/robots.txt": robots("User-agent: *\nDisallow: /private"),
            "s.example/ok": redirect("/private/secret"),
        },
    )
    safe, _ = make(config, site)
    with pytest.raises(RobotsDisallowedError):
        safe.get("https://s.example/ok", max_bytes=1000)
    assert "s.example/private/secret" not in site.sent


@pytest.mark.unit
def test_every_redirect_hop_is_rate_limited_and_reads_the_new_site_robots(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    site = Site(
        dns,
        {
            "s.example/robots.txt": robots("", status=404),
            "s.example/old": redirect("https://other.example/new"),
            "other.example/robots.txt": robots("", status=404),
            "other.example/new": page("moved"),
        },
    )
    safe, limiter = make(config, site)
    got = safe.get("https://s.example/old", max_bytes=1000)
    assert got.content == b"moved"
    assert got.url == "https://other.example/new"
    assert site.sent == [
        "s.example/robots.txt",
        "s.example/old",
        "other.example/robots.txt",
        "other.example/new",
    ]
    assert limiter.hosts == ["s.example", "s.example", "other.example", "other.example"]


@pytest.mark.unit
def test_a_redirect_to_a_private_address_is_blocked(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    dns["evil.example"] = ["10.0.0.5"]
    site = Site(
        dns,
        {
            "s.example/robots.txt": robots("", 404),
            "s.example/a": redirect("http://evil.example/"),
        },
    )
    safe, _ = make(config, site)
    with pytest.raises(BlockedAddressError):
        safe.get("https://s.example/a", max_bytes=1000)
    assert not any(key.startswith("evil.example") for key in site.sent)


@pytest.mark.unit
def test_redirects_are_limited(config: FetchConfig, dns: dict[str, list[str]]) -> None:
    pages = {"s.example/robots.txt": robots("", 404)}
    pages |= {f"s.example/{i}": redirect(f"/{i + 1}") for i in range(MAX_REDIRECTS + 2)}
    safe, _ = make(config, Site(dns, pages))
    with pytest.raises(RedirectLimitError):
        safe.get("https://s.example/0", max_bytes=1000)


@pytest.mark.unit
def test_robots_txt_is_read_once_per_site_whatever_the_spelling(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    site = Site(dns, {"s.example/robots.txt": robots("", status=404)})
    safe, limiter = make(config, site)
    for url in (
        "https://s.example/a",
        "https://S.EXAMPLE/b",
        "https://s.example:443/c",
        "https://user@s.example/d",
    ):
        safe.get(url, max_bytes=1000)
    assert site.sent.count("s.example/robots.txt") == 1
    assert set(limiter.hosts) == {"s.example"}  # one rate-limit key for every spelling


@pytest.mark.unit
def test_robots_txt_redirects_are_followed(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    site = Site(
        dns,
        {
            "s.example/robots.txt": redirect("https://www.s.example/robots.txt"),
            "www.s.example/robots.txt": robots("User-agent: *\nDisallow: /private"),
        },
    )
    safe, _ = make(config, site)
    assert not safe.robots("https://s.example/").allowed("https://s.example/private/x")


@pytest.mark.unit
def test_a_large_robots_txt_uses_the_first_500_kib(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    text = "User-agent: *\nDisallow: /private\n" + "# padding\n" * (
        ROBOTS_MAX_BYTES // 10 + 10
    )
    site = Site(dns, {"s.example/robots.txt": robots(text)})
    safe, _ = make(config, site)
    rules = safe.robots("https://s.example/")
    assert not rules.unreachable
    assert rules.allowed("https://s.example/public")
    assert not rules.allowed("https://s.example/private")


@pytest.mark.unit
def test_the_group_for_our_user_agent_wins(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    text = (
        f"User-agent: {config.robots_agent}\nDisallow: /private\n\n"
        "User-agent: *\nDisallow: /\n"
    )
    safe, _ = make(config, Site(dns, {"s.example/robots.txt": robots(text)}))
    assert safe.robots("https://s.example/").allowed("https://s.example/public")
    assert not safe.robots("https://s.example/").allowed("https://s.example/private/x")


@pytest.mark.unit
def test_robots_txt_lists_the_sitemaps(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    text = "User-agent: *\nAllow: /\nSitemap: https://s.example/sitemap_index.xml\n"
    safe, _ = make(config, Site(dns, {"s.example/robots.txt": robots(text)}))
    assert safe.robots("https://s.example/").sitemaps == [
        "https://s.example/sitemap_index.xml"
    ]


@pytest.mark.unit
def test_unreachable_robots_txt_blocks_everything_and_says_why(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    dns["down.example"] = [PUBLIC_IP]

    def down(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=request)

    safe, _ = make(config, down)
    with pytest.raises(RobotsDisallowedError, match=r"robots\.txt could not be read"):
        safe.get("https://down.example/page", max_bytes=1000)
    assert safe.robots("https://down.example/").unreachable


@pytest.mark.unit
def test_a_blocked_site_is_a_clear_block_not_unreachable_robots(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    dns["evil.example"] = ["10.0.0.5"]
    safe, _ = make(config, Site(dns, {}))
    with pytest.raises(BlockedAddressError):
        safe.get("https://evil.example/page", max_bytes=1000)


@pytest.mark.unit
def test_error_messages_leave_out_user_info_and_query(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    site = Site(dns, {"s.example/robots.txt": robots("User-agent: *\nDisallow: /")})
    safe, _ = make(config, site)
    with pytest.raises(RobotsDisallowedError) as error:
        safe.get("https://alice:pw@s.example/page?token=abc", max_bytes=1000)
    message = str(error.value)
    assert "https://s.example/page" in message
    assert "alice" not in message
    assert "pw" not in message
    assert "token" not in message


@pytest.mark.unit
def test_every_safe_fetcher_client_has_the_guard(config: FetchConfig) -> None:
    with (
        SafeFetcher(config) as default,
        SafeFetcher(
            config, transport=httpx.MockTransport(lambda r: httpx.Response(404))
        ) as test_double,
    ):
        assert guard_request in default.client.event_hooks["request"]
        assert guard_request in test_double.client.event_hooks["request"]


@pytest.mark.unit
@pytest.mark.parametrize("location", ["ftp://s.example/file", "file:///etc/passwd"])
def test_a_redirect_to_a_non_web_scheme_is_a_clear_block(
    config: FetchConfig, dns: dict[str, list[str]], location: str
) -> None:
    site = Site(
        dns,
        {"s.example/robots.txt": robots("", 404), "s.example/a": redirect(location)},
    )
    safe, _ = make(config, site)
    with pytest.raises(BlockedAddressError, match="only http/https"):
        safe.get("https://s.example/a", max_bytes=1000)


@pytest.mark.unit
def test_an_invalid_redirect_target_is_an_invalid_url_error(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    """httpx checks Location itself, before our code sees the answer."""
    site = Site(
        dns,
        {
            "s.example/robots.txt": robots("", 404),
            "s.example/a": redirect("javascript:x"),
        },
    )
    safe, _ = make(config, site)
    with pytest.raises(httpx.InvalidURL):
        safe.get("https://s.example/a", max_bytes=1000)


@pytest.mark.unit
def test_robots_txt_with_an_invalid_redirect_is_unreachable(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    site = Site(dns, {"s.example/robots.txt": redirect("javascript:x")})
    safe, _ = make(config, site)
    rules = safe.robots("https://s.example/")
    assert rules.unreachable
    assert not rules.allowed("https://s.example/page")


@pytest.mark.unit
def test_one_time_limit_covers_the_whole_get(
    config: FetchConfig, dns: dict[str, list[str]], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every hop of one get() shares one deadline; a hop cannot start a new one."""
    pages = {"s.example/robots.txt": robots("", 404), "s.example/0": redirect("/1")}
    pages["s.example/1"] = page("done")
    safe, _ = make(config, Site(dns, pages))
    deadlines: list[float] = []
    original = guard_deadline_scope

    @contextmanager
    def record(deadline: float) -> Iterator[float]:
        with original(deadline) as effective:
            deadlines.append(effective)
            yield effective

    monkeypatch.setattr(client_module, "deadline_scope", record)
    safe.get("https://s.example/0", max_bytes=1000)
    assert len(deadlines) == 3  # robots.txt, /0, /1
    assert len(set(deadlines)) == 1  # one shared deadline

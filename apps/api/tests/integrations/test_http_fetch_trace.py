import httpx
import pytest

from seo_advisor.integrations.http_fetch.client import FetchConfig, HostRateLimiter
from seo_advisor.integrations.http_fetch.robots import (
    RobotsDisallowedError,
    SafeFetcher,
)
from seo_advisor.integrations.http_fetch.trace import trace_scope

PUBLIC_IP = "93.184.215.14"
Page = tuple[int, bytes, dict[str, str]]


class NoWait(HostRateLimiter):
    def __init__(self) -> None:
        super().__init__(min_interval_s=0.0)

    def wait(self, host: str) -> None:
        return None


def fetcher(
    config: FetchConfig, dns: dict[str, list[str]], pages: dict[str, Page]
) -> SafeFetcher:
    for key in pages:
        dns.setdefault(key.split("/", 1)[0], [PUBLIC_IP])

    def handler(request: httpx.Request) -> httpx.Response:
        status, body, headers = pages.get(
            f"{request.url.host}{request.url.path}", (404, b"", {})
        )
        return httpx.Response(status, content=iter([body]), headers=headers)

    return SafeFetcher(config, transport=httpx.MockTransport(handler), limiter=NoWait())


@pytest.mark.unit
def test_each_request_is_recorded_in_order(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    pages: dict[str, Page] = {"s.example/sitemap.xml": (200, b"<urlset/>", {})}
    with fetcher(config, dns, pages) as f, trace_scope() as trace:
        f.get("https://s.example/sitemap.xml", 1000)

    assert [(e.kind, e.url, e.outcome, e.status, e.bytes) for e in trace.events] == [
        ("robots", "https://s.example/robots.txt", "ok", 404, 0),
        ("page", "https://s.example/sitemap.xml", "ok", 200, 9),
    ]
    assert all(e.started_ms >= 0 and e.duration_ms >= 0 for e in trace.events)


@pytest.mark.unit
def test_a_redirect_is_one_event_per_hop(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    pages: dict[str, Page] = {
        "s.example/a": (301, b"", {"Location": "/b"}),
        "s.example/b": (200, b"ok", {}),
    }
    with fetcher(config, dns, pages) as f, trace_scope() as trace:
        f.get("https://s.example/a", 1000)

    assert [(e.url, e.outcome, e.status) for e in trace.events[1:]] == [
        ("https://s.example/a", "redirect", 301),
        ("https://s.example/b", "ok", 200),
    ]


@pytest.mark.unit
def test_a_disallowed_url_is_recorded_and_not_sent(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    pages: dict[str, Page] = {
        "s.example/robots.txt": (200, b"User-agent: *\nDisallow: /x", {})
    }
    with (
        fetcher(config, dns, pages) as f,
        trace_scope() as trace,
        pytest.raises(RobotsDisallowedError),
    ):
        f.get("https://s.example/x", 1000)

    last = trace.events[-1]
    assert (last.kind, last.outcome, last.status) == ("page", "disallowed", None)
    assert "disallowed by robots.txt" in last.detail


@pytest.mark.unit
def test_a_blocked_address_is_recorded(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    dns["inside.example"] = ["10.0.0.5"]
    with (
        fetcher(config, dns, {}) as f,
        trace_scope() as trace,
        pytest.raises(httpx.HTTPError),
    ):
        f.get("https://inside.example/sitemap.xml", 1000)

    assert [(e.kind, e.outcome) for e in trace.events] == [("robots", "blocked")]


@pytest.mark.unit
def test_the_trace_keeps_no_query_and_no_user_info(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    pages: dict[str, Page] = {"s.example/feed": (200, b"x", {})}
    with fetcher(config, dns, pages) as f, trace_scope() as trace:
        f.get("https://user:secret@s.example/feed?token=abc", 1000)

    assert trace.events[-1].url == "https://s.example/feed"


@pytest.mark.unit
def test_a_cached_robots_txt_is_recorded_once_per_trace(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    pages: dict[str, Page] = {
        "s.example/a": (200, b"a", {}),
        "s.example/b": (200, b"b", {}),
    }
    with fetcher(config, dns, pages) as f:
        f.get("https://s.example/a", 1000)  # reads robots.txt; outside any trace
        with trace_scope() as trace:
            f.get("https://s.example/a", 1000)
            f.get("https://s.example/b", 1000)

    assert [(e.kind, e.outcome) for e in trace.events] == [
        ("robots", "cached"),
        ("page", "ok"),
        ("page", "ok"),
    ]


@pytest.mark.unit
def test_without_a_trace_scope_nothing_is_kept(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    pages: dict[str, Page] = {"s.example/a": (200, b"a", {})}
    with fetcher(config, dns, pages) as f:
        f.get("https://s.example/a", 1000)
    with trace_scope() as trace:
        pass
    assert trace.events == []

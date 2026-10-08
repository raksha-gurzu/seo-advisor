from collections import Counter
from pathlib import Path

import httpx
import pytest

from seo_advisor.features.inventory.service import discover_pages
from seo_advisor.features.sites.service import PageTypeRule, SiteSpec, load_site_spec
from seo_advisor.integrations.http_fetch import FetchConfig, SafeFetcher
from seo_advisor.integrations.http_fetch.client import HostRateLimiter

FIXTURES = Path(__file__).parent / "fixtures"
REPO = Path(__file__).parents[4]
PUBLIC_IP = "93.184.215.14"
NS = 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'
Page = tuple[int, bytes]


class NoWait(HostRateLimiter):
    def __init__(self) -> None:
        super().__init__(min_interval_s=0.0)

    def wait(self, host: str) -> None:
        return None


class Web:
    """A fake web: 'host/path' -> (status, body). Records every request sent."""

    def __init__(self, dns: dict[str, list[str]], pages: dict[str, Page]) -> None:
        self.pages = pages
        self.sent: list[str] = []
        for key in pages:
            dns.setdefault(key.split("/", 1)[0], [PUBLIC_IP])

    def __call__(self, request: httpx.Request) -> httpx.Response:
        key = f"{request.url.host}{request.url.path}"
        self.sent.append(key)
        status, body = self.pages.get(key, (404, b""))
        return httpx.Response(status, content=iter([body]))


def run(config: FetchConfig, web: Web, site: SiteSpec):  # type: ignore[no-untyped-def]
    with SafeFetcher(
        config, transport=httpx.MockTransport(web), limiter=NoWait()
    ) as fetcher:
        return discover_pages(fetcher, site)


def urlset(*urls: str) -> bytes:
    items = "".join(f"<url><loc>{u}</loc></url>" for u in urls)
    return f"<urlset {NS}>{items}</urlset>".encode()


def index(*urls: str) -> bytes:
    items = "".join(f"<sitemap><loc>{u}</loc></sitemap>" for u in urls)
    return f"<sitemapindex {NS}>{items}</sitemapindex>".encode()


SITE = SiteSpec(
    tenant="T",
    base_url="https://s.example",
    language="en",
    page_types=[PageTypeRule(pattern="/blog/*", page_type="blog_post")],
)


@pytest.mark.unit
def test_mypipit_inventory_from_the_saved_sitemap(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    site = load_site_spec(REPO / "infra" / "sites" / "mypipit.toml")
    sitemap = (FIXTURES / "mypipit-sitemap.xml").read_bytes()
    web = Web(dns, {"marketplace.mypipit.com/sitemap.xml": (200, sitemap)})
    inventory = run(config, web, site)

    assert web.sent == [
        "marketplace.mypipit.com/robots.txt",
        "marketplace.mypipit.com/sitemap.xml",
    ]
    assert inventory.sitemaps_read == ["https://marketplace.mypipit.com/sitemap.xml"]
    assert inventory.problems == []
    assert len(inventory.pages) == 58
    assert {p.language for p in inventory.pages} == {"en"}
    assert Counter(p.page_type for p in inventory.pages) == {
        "blog_post": 30,
        "listing": 17,
        "blog_category": 5,
        "static": 3,
        "blog_index": 1,
        "listing_index": 1,
        "seller": 1,
    }


@pytest.mark.unit
def test_sitemaps_from_robots_txt_and_their_index_are_read(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    web = Web(
        dns,
        {
            "s.example/robots.txt": (200, b"Sitemap: https://s.example/index.xml\n"),
            "s.example/index.xml": (
                200,
                index("https://s.example/a.xml", "https://s.example/b.xml"),
            ),
            "s.example/a.xml": (200, urlset("https://s.example/blog/one")),
            "s.example/b.xml": (200, urlset("https://s.example/about")),
        },
    )
    inventory = run(config, web, SITE)
    assert inventory.sitemaps_read == [
        "https://s.example/index.xml",
        "https://s.example/a.xml",
        "https://s.example/b.xml",
    ]
    assert [(p.url, p.page_type) for p in inventory.pages] == [
        ("https://s.example/blog/one", "blog_post"),
        ("https://s.example/about", "other"),
    ]
    assert inventory.problems == []


@pytest.mark.unit
def test_a_missing_sitemap_is_a_problem(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    dns["s.example"] = [PUBLIC_IP]
    inventory = run(config, Web(dns, {}), SITE)
    assert inventory.pages == []
    assert [(p.kind, p.detail) for p in inventory.problems] == [
        ("sitemap_unreadable", "HTTP 404")
    ]


@pytest.mark.unit
def test_other_hosts_and_duplicates_are_problems(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    body = urlset(
        "https://s.example/a", "https://other.example/x", "https://s.example/a"
    )
    inventory = run(config, Web(dns, {"s.example/sitemap.xml": (200, body)}), SITE)
    assert [p.url for p in inventory.pages] == ["https://s.example/a"]
    assert [(p.kind, p.url) for p in inventory.problems] == [
        ("url_on_other_host", "https://other.example/x"),
        ("duplicate_url", "https://s.example/a"),
    ]


@pytest.mark.unit
def test_a_nested_index_is_a_problem_and_not_followed(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    web = Web(
        dns,
        {
            "s.example/sitemap.xml": (200, index("https://s.example/inner.xml")),
            "s.example/inner.xml": (200, index("https://s.example/deep.xml")),
        },
    )
    inventory = run(config, web, SITE)
    assert "s.example/deep.xml" not in web.sent
    assert [p.kind for p in inventory.problems] == ["nested_sitemap_index"]


@pytest.mark.unit
@pytest.mark.parametrize(
    ("robots", "body", "kind"),
    [
        (b"User-agent: *\nDisallow: /sitemap.xml\n", urlset(), "sitemap_blocked"),
        (b"", b"<urlset><url>", "sitemap_invalid"),
    ],
)
def test_blocked_and_broken_sitemaps_are_problems(
    config: FetchConfig,
    dns: dict[str, list[str]],
    robots: bytes,
    body: bytes,
    kind: str,
) -> None:
    web = Web(
        dns,
        {"s.example/robots.txt": (200, robots), "s.example/sitemap.xml": (200, body)},
    )
    inventory = run(config, web, SITE)
    assert inventory.pages == []
    assert [p.kind for p in inventory.problems] == [kind]


@pytest.mark.unit
def test_a_sitemap_on_a_private_address_is_never_requested(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    dns["evil.example"] = ["10.0.0.5"]
    web = Web(
        dns, {"s.example/robots.txt": (200, b"Sitemap: http://evil.example/s.xml\n")}
    )
    inventory = run(config, web, SITE)
    assert not any(key.startswith("evil.example") for key in web.sent)
    assert [p.kind for p in inventory.problems] == ["sitemap_on_other_host"]


@pytest.mark.unit
def test_sitemaps_on_other_hosts_are_problems_and_never_requested(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    web = Web(
        dns,
        {
            "s.example/robots.txt": (
                200,
                b"Sitemap: https://s.example/index.xml\n"
                b"Sitemap: https://other.example/a.xml\n",
            ),
            "s.example/index.xml": (200, index("https://third.example/b.xml")),
            "other.example/a.xml": (200, urlset("https://s.example/a")),
            "third.example/b.xml": (200, urlset("https://s.example/b")),
        },
    )
    inventory = run(config, web, SITE)
    assert not any(key.startswith(("other.", "third.")) for key in web.sent)
    assert [(p.kind, p.url) for p in inventory.problems] == [
        ("sitemap_on_other_host", "https://other.example/a.xml"),
        ("sitemap_on_other_host", "https://third.example/b.xml"),
    ]


@pytest.mark.unit
def test_a_page_url_that_is_not_http_is_a_problem(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    body = urlset(
        "javascript://s.example/%0aalert(1)", "http://[::1/x", "https://s.example/a"
    )
    inventory = run(config, Web(dns, {"s.example/sitemap.xml": (200, body)}), SITE)
    assert [p.url for p in inventory.pages] == ["https://s.example/a"]
    assert [(p.kind, p.detail) for p in inventory.problems] == [
        ("url_not_http", ""),
        ("url_not_http", "not a valid URL"),
    ]


@pytest.mark.unit
def test_a_network_error_shows_only_its_type(
    config: FetchConfig, dns: dict[str, list[str]]
) -> None:
    def broken(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/sitemap.xml":
            raise httpx.ConnectError("resolver detail: 10.1.2.3 refused")
        return httpx.Response(404, content=iter([b""]))

    dns["s.example"] = [PUBLIC_IP]
    with SafeFetcher(
        config, transport=httpx.MockTransport(broken), limiter=NoWait()
    ) as fetcher:
        inventory = discover_pages(fetcher, SITE)
    assert [(p.kind, p.detail) for p in inventory.problems] == [
        ("sitemap_unreadable", "ConnectError")
    ]

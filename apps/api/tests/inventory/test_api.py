import uuid
from collections.abc import Iterator

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from seo_advisor.core.api import get_fetcher, get_session
from seo_advisor.features.sites.service import PageTypeRule, SiteSpec, register_site
from seo_advisor.integrations.http_fetch import FetchConfig, SafeFetcher
from seo_advisor.integrations.http_fetch.client import HostRateLimiter
from seo_advisor.main import build_app

PUBLIC_IP = "93.184.215.14"
NS = 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'
SPEC = SiteSpec(
    tenant="T",
    base_url="https://s.example",
    language="en",
    page_types=[
        PageTypeRule(pattern="/blog", page_type="blog_index"),
        PageTypeRule(pattern="/blog/*", page_type="blog_post"),
    ],
)
SITEMAP = (
    f"<urlset {NS}><url><loc>https://s.example/blog/a</loc></url>"
    f"<url><loc>https://other.example/x</loc></url></urlset>"
).encode()


class NoWait(HostRateLimiter):
    def __init__(self) -> None:
        super().__init__(min_interval_s=0.0)

    def wait(self, host: str) -> None:
        return None


@pytest.fixture
def api(
    db: Session, config: FetchConfig, dns: dict[str, list[str]]
) -> Iterator[TestClient]:
    dns["s.example"] = [PUBLIC_IP]

    def web(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/sitemap.xml":
            return httpx.Response(200, content=iter([SITEMAP]))
        return httpx.Response(404, content=iter([b""]))

    fetcher = SafeFetcher(config, transport=httpx.MockTransport(web), limiter=NoWait())
    app = build_app(allowed_hosts=["testserver"])
    app.dependency_overrides[get_session] = lambda: db
    app.dependency_overrides[get_fetcher] = lambda: fetcher
    with TestClient(app) as client:
        yield client
    fetcher.close()


@pytest.mark.integration
def test_a_discovery_returns_pages_problems_and_requests(
    api: TestClient, db: Session
) -> None:
    site = register_site(db, SPEC)
    response = api.post(f"/api/v1/sites/{site.id}/discoveries")
    assert response.status_code == 200
    run = response.json()
    assert run["site_id"] == str(site.id)
    inventory = run["inventory"]
    assert [(p["url"], p["page_type"]) for p in inventory["pages"]] == [
        ("https://s.example/blog/a", "blog_post")
    ]
    assert [p["kind"] for p in inventory["problems"]] == ["url_on_other_host"]
    assert [(r["kind"], r["status"]) for r in run["requests"]] == [
        ("robots", 404),
        ("page", 200),
    ]


@pytest.mark.integration
def test_a_discovery_of_an_unknown_site_is_404(api: TestClient) -> None:
    response = api.post(f"/api/v1/sites/{uuid.uuid4()}/discoveries")
    assert response.status_code == 404


@pytest.mark.integration
def test_the_page_type_of_a_url(api: TestClient, db: Session) -> None:
    site = register_site(db, SPEC)
    response = api.get(
        f"/api/v1/sites/{site.id}/page-type",
        params={"url": "https://s.example/blog/"},
    )
    assert response.json() == {
        "url": "https://s.example/blog/",
        "path": "/blog",
        "page_type": "blog_index",
        "rule_index": 0,
        "pattern": "/blog",
    }


@pytest.mark.integration
def test_a_malformed_url_is_a_422_not_a_500(api: TestClient, db: Session) -> None:
    site = register_site(db, SPEC)
    response = api.get(
        f"/api/v1/sites/{site.id}/page-type", params={"url": "http://[::1/x"}
    )
    assert response.status_code == 422
    assert response.headers["content-type"] == "application/problem+json"

import uuid
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from seo_advisor.core.api import get_session
from seo_advisor.features.sites.service import PageTypeRule, SiteSpec, register_site
from seo_advisor.main import build_app

SPEC = SiteSpec(
    tenant="MyPipit",
    base_url="https://s.example",
    language="en",
    page_types=[PageTypeRule(pattern="/blog/*", page_type="blog_post")],
)


@pytest.fixture
def api(db: Session) -> Iterator[TestClient]:
    app = build_app(allowed_hosts=["testserver"])
    app.dependency_overrides[get_session] = lambda: db
    with TestClient(app) as client:
        yield client


@pytest.mark.integration
def test_sites_are_listed_with_their_tenant(api: TestClient, db: Session) -> None:
    site = register_site(db, SPEC)
    response = api.get("/api/v1/sites")
    assert response.status_code == 200
    listed = [s for s in response.json() if s["id"] == str(site.id)]
    assert listed[0]["tenant_name"] == "MyPipit"
    assert listed[0]["page_types"] == [{"pattern": "/blog/*", "page_type": "blog_post"}]


@pytest.mark.integration
def test_one_site_by_id(api: TestClient, db: Session) -> None:
    site = register_site(db, SPEC)
    response = api.get(f"/api/v1/sites/{site.id}")
    assert response.json()["base_url"] == "https://s.example"


@pytest.mark.integration
def test_an_unknown_site_is_404(api: TestClient) -> None:
    response = api.get(f"/api/v1/sites/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"


@pytest.mark.unit
def test_health() -> None:
    with TestClient(build_app(allowed_hosts=["testserver"])) as client:
        assert client.get("/health").json() == {"status": "ok"}

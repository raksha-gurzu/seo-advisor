import uuid

import pytest
from sqlalchemy.orm import Session

from seo_advisor.features.sites.service import (
    PageTypeRule,
    SiteSpec,
    get_site,
    register_site,
)

SPEC = SiteSpec(
    tenant="MyPipit",
    base_url="https://s.example",
    language="en",
    page_types=[PageTypeRule(pattern="/blog/*", page_type="blog_post")],
)


@pytest.mark.integration
def test_register_creates_the_tenant_and_the_site(db: Session) -> None:
    site = register_site(db, SPEC)
    assert site.base_url == "https://s.example"
    assert site.page_types == SPEC.page_types
    assert uuid.UUID(str(site.id)).version == 7  # uuidv7() from PostgreSQL 18
    assert get_site(db, site.id) == site


@pytest.mark.integration
def test_register_twice_changes_nothing(db: Session) -> None:
    first = register_site(db, SPEC)
    second = register_site(db, SPEC)
    assert second == first  # same ids, same updated_at


@pytest.mark.integration
def test_register_with_new_rules_updates_the_site(db: Session) -> None:
    first = register_site(db, SPEC)
    rules = [PageTypeRule(pattern="/news/*", page_type="news")]
    second = register_site(db, SPEC.model_copy(update={"page_types": rules}))
    assert second.id == first.id
    assert second.page_types == rules
    assert second.updated_at > first.updated_at


@pytest.mark.integration
def test_two_tenants_can_have_the_same_site_address(db: Session) -> None:
    a = register_site(db, SPEC)
    b = register_site(db, SPEC.model_copy(update={"tenant": "Other"}))
    assert a.id != b.id
    assert a.tenant_id != b.tenant_id

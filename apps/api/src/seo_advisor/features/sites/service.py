"""Sites service: the public functions and types that other features may use."""

import tomllib
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from seo_advisor.features.sites import repository
from seo_advisor.features.sites.models import Site
from seo_advisor.features.sites.schemas import (
    PageType,
    PageTypeRule,
    SiteRecord,
    SiteSpec,
)

__all__ = [
    "PageType",
    "PageTypeRule",
    "SiteRecord",
    "SiteSpec",
    "get_site",
    "load_site_spec",
    "register_site",
]


def load_site_spec(path: Path) -> SiteSpec:
    """Read a site file (TOML), for example infra/sites/mypipit.toml."""
    with path.open("rb") as file:
        return SiteSpec.model_validate(tomllib.load(file))


def register_site(session: Session, spec: SiteSpec) -> SiteRecord:
    """Create or update the tenant's site from a site file. Unchanged: no write."""
    tenant = repository.get_or_create_tenant(session, spec.tenant)
    site = repository.save_site(
        session,
        tenant_id=tenant.id,
        base_url=spec.base_url,
        language=spec.language,
        page_types=[rule.model_dump() for rule in spec.page_types],
    )
    session.commit()
    return _record(site)


def get_site(session: Session, site_id: uuid.UUID) -> SiteRecord:
    return _record(repository.get_site(session, site_id))


def _record(site: Site) -> SiteRecord:
    return SiteRecord(
        id=site.id,
        tenant_id=site.tenant_id,
        base_url=site.base_url,
        language=site.language,
        page_types=[PageTypeRule.model_validate(rule) for rule in site.page_types],
        created_at=site.created_at,
        updated_at=site.updated_at,
    )

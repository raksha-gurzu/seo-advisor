"""SQL for the sites feature. Private: other features use service.py."""

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from seo_advisor.features.sites.models import Site, Tenant


def get_or_create_tenant(session: Session, name: str) -> Tenant:
    tenant = session.scalars(select(Tenant).where(Tenant.name == name)).one_or_none()
    if tenant is None:
        tenant = Tenant(name=name)
        session.add(tenant)
        session.flush()
    return tenant


def find_site(session: Session, tenant_id: uuid.UUID, base_url: str) -> Site | None:
    query = select(Site).where(Site.tenant_id == tenant_id, Site.base_url == base_url)
    return session.scalars(query).one_or_none()


def get_site(session: Session, site_id: uuid.UUID) -> Site:
    """The site, or sqlalchemy.exc.NoResultFound."""
    return session.scalars(select(Site).where(Site.id == site_id)).one()


def list_sites(session: Session) -> list[Site]:
    """All sites, by tenant name, then base URL."""
    query = select(Site).join(Site.tenant).order_by(Tenant.name, Site.base_url)
    return list(session.scalars(query))


def save_site(
    session: Session,
    tenant_id: uuid.UUID,
    base_url: str,
    language: str,
    page_types: list[dict[str, Any]],
) -> Site:
    """Insert the site, or update it only if a value changed (then `updated_at`)."""
    site = find_site(session, tenant_id, base_url)
    if site is None:
        site = Site(
            tenant_id=tenant_id,
            base_url=base_url,
            language=language,
            page_types=page_types,
        )
        session.add(site)
    elif (site.language, site.page_types) != (language, page_types):
        site.language = language
        site.page_types = page_types
        site.updated_at = func.clock_timestamp()  # now() is the transaction start
    session.flush()
    session.refresh(site)
    return site

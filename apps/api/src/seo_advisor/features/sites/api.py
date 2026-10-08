"""HTTP routes of the sites feature. Only main.py mounts this router."""

import uuid

from fastapi import APIRouter

from seo_advisor.core.api import SessionDep
from seo_advisor.features.sites import service
from seo_advisor.features.sites.schemas import SiteRecord

router = APIRouter(prefix="/sites", tags=["sites"])


@router.get("")
def list_sites(session: SessionDep) -> list[SiteRecord]:
    return service.list_sites(session)


@router.get("/{site_id}")
def get_site(site_id: uuid.UUID, session: SessionDep) -> SiteRecord:
    return service.get_site(session, site_id)

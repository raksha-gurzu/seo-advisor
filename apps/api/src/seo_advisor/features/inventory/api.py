"""HTTP routes of the inventory feature. Only main.py mounts this router."""

import uuid

from fastapi import APIRouter

from seo_advisor.core.api import FetcherDep, SessionDep
from seo_advisor.features.inventory import service
from seo_advisor.features.inventory.schemas import DiscoveryRun, PageTypeMatch

router = APIRouter(prefix="/sites/{site_id}", tags=["inventory"])


@router.post("/discoveries")
def run_discovery(
    site_id: uuid.UUID, session: SessionDep, fetcher: FetcherDep
) -> DiscoveryRun:
    """Read robots.txt and the sitemaps now (read-only, live) and list the pages."""
    return service.run_discovery(session, fetcher, site_id)


@router.get("/page-type")
def find_page_type(site_id: uuid.UUID, url: str, session: SessionDep) -> PageTypeMatch:
    """Which page-type rule matches this URL. Nothing is fetched."""
    return service.find_page_type(session, site_id, url)

"""Data shapes of the inventory feature."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from seo_advisor.features.sites.service import PageType
from seo_advisor.integrations.http_fetch import FetchEvent


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class SitemapEntry(_Frozen):
    url: str
    lastmod: str = ""  # as written in the sitemap; slice 4 checks it


class ParsedSitemap(_Frozen):
    kind: Literal["urlset", "index"]
    entries: list[SitemapEntry]


class DiscoveredPage(_Frozen):
    url: str
    page_type: PageType
    language: str
    lastmod: str
    sitemap: str  # the sitemap file that listed the page


ProblemKind = Literal[
    "sitemap_blocked",  # robots.txt or the address guard does not allow it
    "sitemap_unreadable",  # HTTP error, too large, network error
    "sitemap_invalid",  # not a valid sitemap file
    "nested_sitemap_index",  # an index inside an index (sitemaps.org does not allow it)
    "sitemap_on_other_host",  # not followed: one site's run reaches only its own host
    "url_on_other_host",  # sitemaps.org: a sitemap lists only URLs on its own host
    "url_not_http",  # a page URL must be http or https
    "duplicate_url",
]


class InventoryProblem(_Frozen):
    kind: ProblemKind
    url: str
    detail: str = ""


class Inventory(_Frozen):
    base_url: str
    sitemaps_read: list[str]
    pages: list[DiscoveredPage]
    problems: list[InventoryProblem]


class DiscoveryRun(_Frozen):
    """One live discovery: the inventory and every request it made."""

    site_id: uuid.UUID
    started_at: datetime
    duration_ms: int
    inventory: Inventory
    requests: list[FetchEvent]


class PageTypeMatch(_Frozen):
    """Which rule gives a URL its page type. No match: "other", no rule."""

    url: str
    path: str  # the path that the rules compare
    page_type: PageType
    rule_index: int | None = None
    pattern: str | None = None

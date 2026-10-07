"""Data shapes of the inventory feature."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from seo_advisor.features.sites.service import PageType


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
    "url_on_other_host",  # sitemaps.org: a sitemap lists only URLs on its own host
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

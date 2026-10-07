"""Inventory service: the public functions that other features may use."""

from typing import Protocol
from urllib.parse import urlsplit

import httpx

from seo_advisor.features.inventory.page_types import page_type_of
from seo_advisor.features.inventory.schemas import (
    DiscoveredPage,
    Inventory,
    InventoryProblem,
    ParsedSitemap,
)
from seo_advisor.features.inventory.sitemaps import (
    SITEMAP_MAX_BYTES,
    InvalidSitemapError,
    parse_sitemap,
)
from seo_advisor.features.sites.service import PageTypeRule
from seo_advisor.integrations.http_fetch import (
    BlockedAddressError,
    ContentEncodingError,
    RedirectLimitError,
    RobotsDisallowedError,
    SafeFetcher,
)


class SiteRules(Protocol):
    """What discover_pages needs of a site: a site file or a stored site."""

    @property
    def base_url(self) -> str: ...
    @property
    def language(self) -> str: ...
    @property
    def page_types(self) -> list[PageTypeRule]: ...


def discover_pages(fetcher: SafeFetcher, site: SiteRules) -> Inventory:
    """All pages that the site's sitemaps list, with page type and language.

    Sitemaps come from robots.txt `Sitemap:` lines, else from /sitemap.xml. A problem
    with one sitemap does not stop the others: it goes into `problems`.
    """
    listed = fetcher.robots(site.base_url).sitemaps
    queue = [(url, True) for url in listed or [f"{site.base_url}/sitemap.xml"]]
    host = urlsplit(site.base_url).hostname
    seen_files: set[str] = set()
    seen_urls: set[str] = set()
    read: list[str] = []
    pages: list[DiscoveredPage] = []
    problems: list[InventoryProblem] = []

    while queue:
        sitemap_url, top_level = queue.pop(0)
        if sitemap_url in seen_files:
            continue
        seen_files.add(sitemap_url)
        parsed = _read(fetcher, sitemap_url, problems)
        if parsed is None:
            continue
        read.append(sitemap_url)
        if parsed.kind == "index":
            if not top_level:
                problems.append(
                    InventoryProblem(kind="nested_sitemap_index", url=sitemap_url)
                )
                continue
            queue.extend((entry.url, False) for entry in parsed.entries)
            continue
        for entry in parsed.entries:
            if urlsplit(entry.url).hostname != host:
                problems.append(
                    InventoryProblem(kind="url_on_other_host", url=entry.url)
                )
            elif entry.url in seen_urls:
                problems.append(InventoryProblem(kind="duplicate_url", url=entry.url))
            else:
                seen_urls.add(entry.url)
                pages.append(
                    DiscoveredPage(
                        url=entry.url,
                        page_type=page_type_of(entry.url, site.page_types),
                        language=site.language,
                        lastmod=entry.lastmod,
                        sitemap=sitemap_url,
                    )
                )
    return Inventory(
        base_url=site.base_url, sitemaps_read=read, pages=pages, problems=problems
    )


def _read(
    fetcher: SafeFetcher, url: str, problems: list[InventoryProblem]
) -> ParsedSitemap | None:
    """One sitemap file, or None after one problem is added to `problems`."""
    try:
        got = fetcher.get(url, SITEMAP_MAX_BYTES)
    except (RobotsDisallowedError, BlockedAddressError) as exc:
        problems.append(
            InventoryProblem(kind="sitemap_blocked", url=url, detail=str(exc))
        )
        return None
    except (
        httpx.HTTPError,
        httpx.InvalidURL,
        RedirectLimitError,
        ContentEncodingError,
    ) as exc:
        detail = f"{type(exc).__name__}: {exc}"
        problems.append(
            InventoryProblem(kind="sitemap_unreadable", url=url, detail=detail)
        )
        return None
    if got.status != 200:
        detail = f"HTTP {got.status}"
        problems.append(
            InventoryProblem(kind="sitemap_unreadable", url=url, detail=detail)
        )
        return None
    if got.too_large:
        detail = "larger than 50 MB"
        problems.append(
            InventoryProblem(kind="sitemap_unreadable", url=url, detail=detail)
        )
        return None
    try:
        return parse_sitemap(got.content)
    except InvalidSitemapError as exc:
        problems.append(
            InventoryProblem(kind="sitemap_invalid", url=url, detail=str(exc))
        )
        return None

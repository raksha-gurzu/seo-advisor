"""Inventory service: the public functions that other features may use."""

import time
import uuid
from datetime import UTC, datetime
from typing import Protocol
from urllib.parse import SplitResult, urlsplit

import httpx
from sqlalchemy.orm import Session

from seo_advisor.core.errors import InvalidInputError
from seo_advisor.features.inventory.page_types import match_page_type, page_type_of
from seo_advisor.features.inventory.schemas import (
    DiscoveredPage,
    DiscoveryRun,
    Inventory,
    InventoryProblem,
    PageTypeMatch,
    ParsedSitemap,
)
from seo_advisor.features.inventory.sitemaps import (
    SITEMAP_MAX_BYTES,
    InvalidSitemapError,
    parse_sitemap,
)
from seo_advisor.features.sites.service import PageTypeRule, get_site
from seo_advisor.integrations.http_fetch import (
    BlockedAddressError,
    ContentEncodingError,
    RedirectLimitError,
    RobotsDisallowedError,
    SafeFetcher,
    trace_scope,
)

__all__ = [
    "DiscoveryRun",
    "Inventory",
    "PageTypeMatch",
    "SiteRules",
    "discover_pages",
    "find_page_type",
    "run_discovery",
]


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
    host = _host(site.base_url)
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
        if _host(sitemap_url) != host:
            # A hostile robots.txt or index could name thousands of other hosts.
            problems.append(
                InventoryProblem(kind="sitemap_on_other_host", url=sitemap_url)
            )
            continue
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
            parts = _split(entry.url)
            if parts is None or parts.scheme not in ("http", "https"):
                detail = "not a valid URL" if parts is None else ""
                problems.append(
                    InventoryProblem(kind="url_not_http", url=entry.url, detail=detail)
                )
            elif parts.hostname != host:
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


def run_discovery(
    session: Session, fetcher: SafeFetcher, site_id: uuid.UUID
) -> DiscoveryRun:
    """Discover a stored site's pages live (read-only) and record every request."""
    site = get_site(session, site_id)
    # End the read transaction now: the network part can take minutes, and an open
    # transaction would hold a pooled connection all that time.
    session.close()
    started_at = datetime.now(UTC)
    begin = time.monotonic()
    with trace_scope() as trace:
        inventory = discover_pages(fetcher, site)
    return DiscoveryRun(
        site_id=site.id,
        started_at=started_at,
        duration_ms=round((time.monotonic() - begin) * 1000),
        inventory=inventory,
        requests=trace.events,
    )


def find_page_type(session: Session, site_id: uuid.UUID, url: str) -> PageTypeMatch:
    """Which of the site's rules gives this URL its page type."""
    rules = get_site(session, site_id).page_types
    try:
        return match_page_type(url, rules)
    except ValueError as exc:  # urlsplit: for example "http://[::1/x"
        raise InvalidInputError(f"not a valid URL: {exc}") from None


def _split(url: str) -> SplitResult | None:
    """The URL's parts, or None if it cannot be parsed. The caller reports a problem."""
    try:
        return urlsplit(url)
    except ValueError:  # for example "http://[::1/x"
        return None


def _host(url: str) -> str | None:
    """The URL's host. An unparseable URL has none, so it never matches a site host."""
    parts = _split(url)
    return None if parts is None else parts.hostname


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
        # Only the error type: a message can hold resolver or TLS system details.
        detail = type(exc).__name__
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

"""Page type of a URL, from the site's pattern rules (data, not code)."""

import re
from functools import lru_cache
from urllib.parse import urlsplit

from seo_advisor.features.inventory.schemas import PageTypeMatch
from seo_advisor.features.sites.service import PageType, PageTypeRule

OTHER: PageType = "other"


@lru_cache(maxsize=1024)
def _compile(pattern: str) -> re.Pattern[str]:
    parts = [p for p in pattern.strip("/").split("/") if p]
    body = "/".join("[^/]+" if part == "*" else re.escape(part) for part in parts)
    return re.compile(f"/{body}")


def page_type_of(url: str, rules: list[PageTypeRule]) -> PageType:
    """The page type of the first rule that matches the URL path, else "other"."""
    return match_page_type(url, rules).page_type


def match_page_type(url: str, rules: list[PageTypeRule]) -> PageTypeMatch:
    """The first rule that matches the URL path, and the path that was compared."""
    path = urlsplit(url).path or "/"
    if len(path) > 1:
        path = path.rstrip("/")
    for index, rule in enumerate(rules):
        if _compile(rule.pattern).fullmatch(path):
            return PageTypeMatch(
                url=url,
                path=path,
                page_type=rule.page_type,
                rule_index=index,
                pattern=rule.pattern,
            )
    return PageTypeMatch(url=url, path=path, page_type=OTHER)

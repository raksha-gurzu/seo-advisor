"""Page type of a URL, from the site's pattern rules (data, not code)."""

import re
from functools import lru_cache
from urllib.parse import urlsplit

from seo_advisor.features.sites.service import PageType, PageTypeRule

OTHER: PageType = "other"


@lru_cache(maxsize=1024)
def _compile(pattern: str) -> re.Pattern[str]:
    parts = [p for p in pattern.strip("/").split("/") if p]
    body = "/".join("[^/]+" if part == "*" else re.escape(part) for part in parts)
    return re.compile(f"/{body}")


def page_type_of(url: str, rules: list[PageTypeRule]) -> PageType:
    """The page type of the first rule that matches the URL path, else "other"."""
    path = urlsplit(url).path or "/"
    if len(path) > 1:
        path = path.rstrip("/")
    for rule in rules:
        if _compile(rule.pattern).fullmatch(path):
            return rule.page_type
    return OTHER

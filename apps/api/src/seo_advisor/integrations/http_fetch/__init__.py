"""Safe outbound HTTP: SSRF guard, size and time limits, rate limit, robots.txt.

Every outbound fetch goes through this package (CLAUDE.md, Security).
Reused from SEOAdvisor (src/seo_engine/providers/base.py and fetcher.py).
"""

from seo_advisor.integrations.http_fetch.client import (
    ContentEncodingError,
    Download,
    FetchConfig,
)
from seo_advisor.integrations.http_fetch.guard import BlockedAddressError
from seo_advisor.integrations.http_fetch.robots import (
    RedirectLimitError,
    RobotsDisallowedError,
    RobotsRules,
    SafeFetcher,
)

__all__ = [
    "BlockedAddressError",
    "ContentEncodingError",
    "Download",
    "FetchConfig",
    "RedirectLimitError",
    "RobotsDisallowedError",
    "RobotsRules",
    "SafeFetcher",
]

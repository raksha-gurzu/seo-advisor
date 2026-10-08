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
from seo_advisor.integrations.http_fetch.trace import (
    FetchEvent,
    FetchTrace,
    trace_scope,
)

__all__ = [
    "BlockedAddressError",
    "ContentEncodingError",
    "Download",
    "FetchConfig",
    "FetchEvent",
    "FetchTrace",
    "RedirectLimitError",
    "RobotsDisallowedError",
    "RobotsRules",
    "SafeFetcher",
    "trace_scope",
]

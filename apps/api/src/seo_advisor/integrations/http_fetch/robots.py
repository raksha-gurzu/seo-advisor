"""robots.txt (RFC 9309) and the SafeFetcher that obeys it on every redirect hop."""

import time
from collections.abc import Callable
from dataclasses import dataclass
from types import TracebackType
from typing import Self
from urllib.parse import urljoin

import httpx
from protego import Protego

from seo_advisor.integrations.http_fetch.client import (
    ContentEncodingError,
    Download,
    FetchConfig,
    HostRateLimiter,
    bounded_get,
    public_client,
)
from seo_advisor.integrations.http_fetch.guard import (
    DEFAULT_PORTS,
    BlockedAddressError,
    deadline_scope,
    require_web_scheme,
)

DISALLOW_ALL = "User-agent: *\nDisallow: /"
ROBOTS_MAX_BYTES = 512_000  # RFC 9309 §2.5: parse at least the first 500 KiB
ROBOTS_MAX_AGE_S = (
    24 * 3600
)  # RFC 9309 §2.4: do not use a cached copy for over 24 hours
MAX_REDIRECTS = (
    5  # RFC 9309 §2.3.1.2 asks for at least 5 for robots.txt; R4 §11.6: a cap
)


class RobotsDisallowedError(Exception):
    """robots.txt does not allow this URL, or robots.txt could not be read."""


class RedirectLimitError(Exception):
    """More than MAX_REDIRECTS redirects in a row."""


def robots_body(status: int | None, text: str) -> tuple[str, bool]:
    """(the rules we obey, robots.txt was unreachable) for one robots.txt answer.

    - No answer, 5xx or 429: disallow everything, temporary (RFC 9309 §2.3.1.4).
    - A final 3xx (no redirect target): disallow everything, temporary. We are strict.
    - 401/403: disallow everything. The RFC allows crawling here; we are stricter.
    - Other 4xx (404, 410): no rules, so everything is allowed.
    """
    if status is None or status >= 500 or status == 429 or 300 <= status < 400:
        return DISALLOW_ALL, True
    if status in (401, 403):
        return DISALLOW_ALL, False
    if status >= 400:
        return "", False
    return text, False


@dataclass(frozen=True)
class RobotsRules:
    """The robots.txt rules of one site (origin)."""

    parser: Protego
    agent: str
    status: int | None
    unreachable: bool

    def allowed(self, url: str) -> bool:
        return bool(self.parser.can_fetch(url, self.agent))

    @property
    def sitemaps(self) -> list[str]:
        return list(self.parser.sitemaps)


def origin_key(url: str) -> str:
    """scheme://host:port in one spelling: lower-case host, port, no user info."""
    parts = httpx.URL(url)
    return f"{parts.scheme}://{parts.host}:{parts.port or DEFAULT_PORTS[parts.scheme]}"


def display_url(url: str) -> str:
    """The URL for messages: no user info and no query, which can hold secrets."""
    parts = httpx.URL(url)
    return f"{parts.scheme}://{parts.netloc.decode('ascii')}{parts.path}"


class SafeFetcher:
    """Fetch URLs safely: SSRF guard, robots.txt and rate limit on every redirect hop,
    size and time limits."""

    def __init__(
        self,
        config: FetchConfig,
        transport: httpx.BaseTransport | None = None,
        limiter: HostRateLimiter | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.config = config
        self.client = public_client(config, transport)
        self.limiter = limiter or HostRateLimiter(config.min_delay_s)
        self._clock = clock
        self._robots: dict[str, tuple[float, RobotsRules]] = {}

    def robots(self, url: str) -> RobotsRules:
        """The site's robots.txt rules: read once per origin, kept for 24 hours."""
        require_web_scheme(url)
        key = origin_key(url)
        cached = self._robots.get(key)
        if cached is not None and self._clock() - cached[0] < ROBOTS_MAX_AGE_S:
            return cached[1]
        robots_url = urljoin(display_url(url), "/robots.txt")
        status: int | None
        try:
            got = self._follow(robots_url, ROBOTS_MAX_BYTES, keep_head=True, obey=False)
        except BlockedAddressError:
            raise  # an SSRF block is never "robots.txt unreachable"
        except (
            httpx.HTTPError,
            httpx.InvalidURL,
            ContentEncodingError,
            RedirectLimitError,
        ):
            # RFC 9309 §2.3.1.4: unreachable means disallow everything. More than 5
            # redirects or an invalid redirect target may count as "unavailable"
            # (allow all); we are stricter.
            status, text = None, ""
        else:
            status = got.status
            text = got.content.decode("utf-8", errors="replace")  # RFC 9309: UTF-8
            if got.too_large:
                text = text.rsplit("\n", 1)[0]  # drop the line that the limit cut
        body, unreachable = robots_body(status, text)
        rules = RobotsRules(
            Protego.parse(body), self.config.robots_agent, status, unreachable
        )
        self._robots[key] = (self._clock(), rules)
        return rules

    def get(self, url: str, max_bytes: int) -> Download:
        """GET a URL; follow up to MAX_REDIRECTS redirects. Each hop must be allowed."""
        return self._follow(url, max_bytes, keep_head=False, obey=True)

    def _follow(
        self, url: str, max_bytes: int, *, keep_head: bool, obey: bool
    ) -> Download:
        """One total time limit for all hops, and for the robots.txt reads inside them.

        Deadlines use the real monotonic clock, like bounded_get; `clock` is only the
        age of cached robots.txt rules.
        """
        start = url
        with deadline_scope(time.monotonic() + self.config.deadline_s):
            for _ in range(MAX_REDIRECTS + 1):
                require_web_scheme(url)
                if obey:
                    self._require_allowed(url)
                self.limiter.wait(httpx.URL(url).host)
                got = bounded_get(
                    self.client,
                    url,
                    max_bytes,
                    self.config.deadline_s,
                    keep_head=keep_head,
                )
                if got.location is None:
                    return got
                url = urljoin(url, got.location)
        raise RedirectLimitError(
            f"{display_url(start)}: more than {MAX_REDIRECTS} redirects"
        )

    def _require_allowed(self, url: str) -> None:
        rules = self.robots(url)
        if not rules.allowed(url):
            reason = (
                "robots.txt could not be read"
                if rules.unreachable
                else "disallowed by robots.txt"
            )
            raise RobotsDisallowedError(f"{display_url(url)}: {reason}")

    def close(self) -> None:
        self.client.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

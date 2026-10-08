"""A record of each request that SafeFetcher makes, for the activity view.

The record holds no body, no headers, no query and no user info: only what the owner
needs to see what happened (URL, status, size, time, the reason for a block).
"""

import time
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Literal

from pydantic import BaseModel, ConfigDict

FetchKind = Literal["robots", "page"]
FetchOutcome = Literal[
    "ok",  # a final answer (any status that is not a redirect)
    "redirect",  # a 3xx with a Location; the next hop is its own event
    "too_large",  # the body passed its size limit
    "cached",  # robots.txt rules came from the 24-hour cache; nothing was sent
    "disallowed",  # robots.txt does not allow the URL; nothing was sent
    "blocked",  # the SSRF guard stopped it (scheme, port or address); nothing was sent
    "error",  # network error, timeout or a broken body
]


class FetchEvent(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: FetchKind
    url: str  # display_url: no user info, no query
    outcome: FetchOutcome
    status: int | None
    bytes: int
    started_ms: int  # from the start of the trace
    waited_ms: int  # rate-limit wait before the request
    duration_ms: int  # the request itself, after the wait
    detail: str = ""


class FetchTrace:
    """The events of one trace scope, in the order they happened."""

    def __init__(self) -> None:
        self.start = time.monotonic()
        self.events: list[FetchEvent] = []
        self.robots_shown: set[str] = set()  # origins with a robots.txt event

    def ms_since_start(self, moment: float) -> int:
        return round((moment - self.start) * 1000)


_current: ContextVar[FetchTrace | None] = ContextVar("fetch_trace", default=None)


@contextmanager
def trace_scope() -> Iterator[FetchTrace]:
    """Record every SafeFetcher request made inside this block (this thread/task)."""
    trace = FetchTrace()
    token = _current.set(trace)
    try:
        yield trace
    finally:
        _current.reset(token)


def current_trace() -> FetchTrace | None:
    """The open trace, or None when no caller asked for one."""
    return _current.get()

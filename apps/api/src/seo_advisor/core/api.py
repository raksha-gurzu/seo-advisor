"""Shared API parts: request IDs, RFC 9457 errors and request dependencies.

Every error leaves the API as `application/problem+json` with the request ID. A 500
never shows its message or stack trace: the log has them, with the same request ID.
"""

import logging
import re
import uuid
from collections.abc import Iterator
from http import HTTPStatus
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, sessionmaker
from starlette.exceptions import HTTPException
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from seo_advisor.core.errors import InvalidInputError, NotFoundError
from seo_advisor.integrations.http_fetch import SafeFetcher

__all__ = [
    "FetcherDep",
    "InvalidInputError",
    "NotFoundError",
    "SessionDep",
    "install_api_basics",
]

PROBLEM_JSON = "application/problem+json"
REQUEST_ID_HEADER = "x-request-id"
# A caller's ID is kept only if it is short and plain; else it could forge log lines.
_SAFE_REQUEST_ID = re.compile(r"[A-Za-z0-9._-]{1,64}")

log = logging.getLogger(__name__)


class RequestIdMiddleware:
    """Give each request an ID, in `request.state.request_id` and in the response."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        incoming = dict(scope["headers"]).get(REQUEST_ID_HEADER.encode(), b"")
        text = incoming.decode("latin-1")
        request_id = text if _SAFE_REQUEST_ID.fullmatch(text) else str(uuid.uuid4())
        scope.setdefault("state", {})["request_id"] = request_id

        async def send_with_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                if not any(name == REQUEST_ID_HEADER.encode() for name, _ in headers):
                    headers.append((REQUEST_ID_HEADER.encode(), request_id.encode()))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_id)


def problem(request: Request, status: int, detail: str, **extra: Any) -> JSONResponse:
    """An RFC 9457 problem document."""
    request_id = getattr(request.state, "request_id", "")
    body = {
        "type": "about:blank",
        "title": HTTPStatus(status).phrase,
        "status": status,
        "detail": detail,
        "instance": request.url.path,
        "request_id": request_id,
        **extra,
    }
    headers = {REQUEST_ID_HEADER: request_id} if request_id else None
    return JSONResponse(body, status, headers=headers, media_type=PROBLEM_JSON)


async def _http_error(request: Request, exc: HTTPException) -> JSONResponse:
    response = problem(request, exc.status_code, str(exc.detail))
    response.headers.update(exc.headers or {})  # for example Allow on a 405
    return response


async def _not_found(request: Request, exc: NotFoundError) -> JSONResponse:
    return problem(request, 404, str(exc))


async def _invalid_input(request: Request, exc: InvalidInputError) -> JSONResponse:
    return problem(request, 422, str(exc))


async def _invalid_request(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    # Field, message and kind only: the input value can be personal or secret.
    errors = [
        {"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]}
        for e in exc.errors()
    ]
    return problem(request, 422, "The request is not valid.", errors=errors)


async def _unexpected(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "")
    log.exception("unhandled error, request_id=%s", request_id)
    return problem(request, 500, "An unexpected error occurred.")


def install_api_basics(app: FastAPI, allowed_hosts: list[str]) -> None:
    """Add the host check, the request-ID middleware and the problem+json handlers.

    The host check stops DNS rebinding: a hostile web page that points its own name
    at 127.0.0.1 sends a Host header that is not in `allowed_hosts`.
    """
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
    # The decorator form takes handlers typed with their own exception class.
    app.exception_handler(HTTPException)(_http_error)
    app.exception_handler(RequestValidationError)(_invalid_request)
    app.exception_handler(NotFoundError)(_not_found)
    app.exception_handler(InvalidInputError)(_invalid_input)
    app.exception_handler(Exception)(_unexpected)


# --- Request dependencies ------------------------------------------------------
# main.py puts the session factory and the fetcher on app.state at start-up.
# Tests replace these functions with app.dependency_overrides.


def get_session(request: Request) -> Iterator[Session]:
    factory: sessionmaker[Session] = request.app.state.sessions
    with factory() as session:
        yield session


def get_fetcher(request: Request) -> SafeFetcher:
    """The app's one fetcher: one rate limit per host and one robots.txt cache."""
    fetcher: SafeFetcher = request.app.state.fetcher
    return fetcher


SessionDep = Annotated[Session, Depends(get_session)]
FetcherDep = Annotated[SafeFetcher, Depends(get_fetcher)]

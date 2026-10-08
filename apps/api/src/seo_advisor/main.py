"""Build the API app and mount the feature routers.

Run: `mise run dev:api` (uvicorn calls `app_from_env`).
"""

from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute

from seo_advisor.core.api import install_api_basics
from seo_advisor.core.config import Settings, load_settings
from seo_advisor.core.db import make_engine, make_session_factory
from seo_advisor.features.inventory.api import router as inventory_router
from seo_advisor.features.sites.api import router as sites_router
from seo_advisor.integrations.http_fetch import FetchConfig, SafeFetcher

Lifespan = Callable[[FastAPI], AbstractAsyncContextManager[None]]

# The API listens on 127.0.0.1 only; the Vite proxy keeps the browser's Host header.
LOCAL_HOSTS = ["127.0.0.1", "localhost"]


def build_app(allowed_hosts: list[str], lifespan: Lifespan | None = None) -> FastAPI:
    """The routes, middleware and error handlers. No database or network yet."""
    app = FastAPI(
        title="seo-advisor API",
        version="0.1.0",
        lifespan=lifespan,
        # The function name is the operation ID, so the TS client has stable names.
        generate_unique_id_function=_operation_id,
    )
    install_api_basics(app, allowed_hosts)

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    v1 = APIRouter(prefix="/api/v1")
    v1.include_router(sites_router)
    v1.include_router(inventory_router)
    app.include_router(v1)
    return app


def create_app(settings: Settings) -> FastAPI:
    """The app with its database and its one SafeFetcher."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        engine = make_engine(settings.database_url)
        app.state.sessions = make_session_factory(engine)
        with SafeFetcher(FetchConfig.from_settings(settings)) as fetcher:
            app.state.fetcher = fetcher
            yield
        engine.dispose()

    return build_app(LOCAL_HOSTS, lifespan)


def app_from_env() -> FastAPI:
    """uvicorn factory: settings come from the environment (.env via mise)."""
    return create_app(load_settings())


def _operation_id(route: APIRoute) -> str:
    return route.name

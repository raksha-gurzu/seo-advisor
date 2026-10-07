import socket
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from testcontainers.community.postgres import PostgresContainer

from seo_advisor.integrations.http_fetch.client import FetchConfig

PUBLIC_IP = "93.184.215.14"


@pytest.fixture
def config() -> FetchConfig:
    return FetchConfig(
        user_agent="seo-advisor-test/0.1",
        robots_agent="seo-advisor-test",
        timeout_s=5.0,
        deadline_s=30.0,
        min_delay_s=1.0,
    )


@pytest.fixture
def dns(monkeypatch: pytest.MonkeyPatch) -> dict[str, list[str]]:
    """Fake DNS for one test: no test sends a real DNS query. Add host -> addresses."""
    answers: dict[str, list[str]] = {}

    def getaddrinfo(
        host: str, port: int | None, *args: Any, **kwargs: Any
    ) -> list[Any]:
        if host not in answers:
            raise socket.gaierror("no such host")
        return [(0, 0, 0, "", (a, port or 0)) for a in answers[host]]

    monkeypatch.setattr(socket, "getaddrinfo", getaddrinfo)
    return answers


# --- Database (integration tests) -------------------------------------------------

POSTGRES_IMAGE = (
    "pgvector/pgvector:0.8.7-pg18-trixie"  # same tag as infra/docker-compose.yml
)
REPO = Path(__file__).parents[3]


def alembic_config(database_url: str) -> Config:
    config = Config(str(REPO / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    return config


@pytest.fixture
def migration_config(database_url: str) -> Config:
    return alembic_config(database_url)


@pytest.fixture(scope="session")
def database_url() -> Iterator[str]:
    """One PostgreSQL container for the test session, migrated to the latest version."""
    with PostgresContainer(POSTGRES_IMAGE, driver="psycopg") as postgres:
        url = postgres.get_connection_url()
        command.upgrade(alembic_config(url), "head")
        yield url


@pytest.fixture(scope="session")
def engine(database_url: str) -> Iterator[Engine]:
    engine = create_engine(database_url)
    yield engine
    engine.dispose()


@pytest.fixture
def db(engine: Engine) -> Iterator[Session]:
    """A session inside a transaction that is rolled back after the test.

    Code under test can commit: commits become SAVEPOINTs of the outer transaction.
    """
    with engine.connect() as connection:
        outer = connection.begin()
        session = Session(bind=connection, join_transaction_mode="create_savepoint")
        try:
            yield session
        finally:
            session.close()
            outer.rollback()

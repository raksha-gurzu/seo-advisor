"""Alembic env. Imports every feature's models: autogenerate sees all tables."""

from alembic import context
from sqlalchemy import Connection, create_engine

import seo_advisor.features.sites.models  # noqa: F401  (registers the tables)
from seo_advisor.core.config import load_settings
from seo_advisor.core.db import Base

config = context.config
target_metadata = Base.metadata


def database_url() -> str:
    """Tests set sqlalchemy.url on the config; else DATABASE_URL from Settings."""
    url = config.get_main_option("sqlalchemy.url")
    return url or load_settings().database_url.get_secret_value()


def run(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    context.configure(
        url=database_url(), target_metadata=target_metadata, literal_binds=True
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = create_engine(database_url())
    with engine.connect() as connection:
        run(connection)
    engine.dispose()

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, inspect


@pytest.mark.integration
def test_the_models_and_the_migrations_agree(migration_config: Config) -> None:
    """`alembic check` fails if a model changed without a migration."""
    command.check(migration_config)


@pytest.mark.integration
def test_the_first_migration_creates_the_tables(engine: Engine) -> None:
    tables = set(inspect(engine).get_table_names())
    assert {"tenants", "sites"} <= tables

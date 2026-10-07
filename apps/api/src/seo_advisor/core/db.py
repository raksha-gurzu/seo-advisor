"""Database base: declarative Base with name rules, ID and time columns, engine."""

import uuid
from datetime import datetime

from pydantic import SecretStr
from sqlalchemy import DateTime, Engine, MetaData, Uuid, create_engine, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

# Alembic "The Importance of Naming Constraints" (R4 §13.2). Set before any migration.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",  # all columns of the rule
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class IdMixin:
    """A uuid primary key made by PostgreSQL 18 `uuidv7()`: time-ordered (RFC 9562)."""

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("uuidv7()")
    )


class TimestampMixin:
    """`timestamptz` columns set by the database clock (UTC)."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


def make_engine(database_url: SecretStr) -> Engine:
    return create_engine(database_url.get_secret_value(), pool_pre_ping=True)


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(engine, expire_on_commit=False)

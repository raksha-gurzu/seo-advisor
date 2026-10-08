"""Tables of the sites feature. Private: other features use service.py."""

import uuid
from typing import Any

from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from seo_advisor.core.db import Base, IdMixin, TimestampMixin


class Tenant(IdMixin, TimestampMixin, Base):
    """A client company. Every other row belongs to one tenant."""

    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(Text, unique=True)


class Site(IdMixin, TimestampMixin, Base):
    """A website of a tenant. Its `id` is the `site_id` of every row about the site."""

    __tablename__ = "sites"
    __table_args__ = (UniqueConstraint("tenant_id", "base_url"),)

    # No separate index: the unique rule (tenant_id, base_url) starts with tenant_id.
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"))
    base_url: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(Text)
    page_types: Mapped[list[dict[str, Any]]] = mapped_column(JSONB)
    tenant: Mapped[Tenant] = relationship(lazy="joined")

"""create tenants and sites

Revision ID: 77d78514aaf7
Revises:
Create Date: 2026-10-07 12:02:35.191388+00:00

Tables of the sites feature: tenants (client companies) and their sites.
IDs: uuidv7() (PostgreSQL 18). Times: timestamptz. Read and edited after autogenerate.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "77d78514aaf7"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("id", sa.Uuid(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tenants")),
        sa.UniqueConstraint("name", name=op.f("uq_tenants_name")),
    )
    op.create_table(
        "sites",
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("base_url", sa.Text(), nullable=False),
        sa.Column("language", sa.Text(), nullable=False),
        sa.Column(
            "page_types", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("id", sa.Uuid(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["tenants.id"], name=op.f("fk_sites_tenant_id_tenants")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sites")),
        sa.UniqueConstraint(
            "tenant_id", "base_url", name=op.f("uq_sites_tenant_id_base_url")
        ),
    )


def downgrade() -> None:
    op.drop_table("sites")
    op.drop_table("tenants")

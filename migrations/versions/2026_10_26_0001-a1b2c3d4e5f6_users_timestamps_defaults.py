"""users timestamps and defaults

Revision ID: a1b2c3d4e5f6
Revises: d2a3e16acd64
Create Date: 2026-10-26 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "d2a3e16acd64"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.execute("UPDATE users SET updated_at = created_at WHERE updated_at IS NULL")
    op.execute("UPDATE users SET is_active = true WHERE is_active IS NULL")
    op.execute("UPDATE users SET is_admin = false WHERE is_admin IS NULL")

    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "is_active",
        existing_type=sa.Boolean(),
        server_default=sa.true(),
        existing_nullable=True,
        nullable=False,
    )
    op.alter_column(
        "users",
        "is_admin",
        existing_type=sa.Boolean(),
        server_default=sa.false(),
        existing_nullable=True,
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "is_admin",
        existing_type=sa.Boolean(),
        server_default=None,
        existing_nullable=False,
        nullable=True,
    )
    op.alter_column(
        "users",
        "is_active",
        existing_type=sa.Boolean(),
        server_default=None,
        existing_nullable=False,
        nullable=True,
    )
    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=None,
        existing_nullable=False,
    )
    op.drop_column("users", "updated_at")

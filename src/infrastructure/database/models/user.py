from datetime import UTC, datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.base_model import Base


class UserModel(Base):
    """SQLAlchemy-модель пользователя."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(sa.String(length=128), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(sa.String, nullable=False)
    email: Mapped[str | None] = mapped_column(sa.String(512), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=sa.func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=sa.func.now(),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean,
        default=True,
        server_default=sa.true(),
        nullable=False,
    )
    is_admin: Mapped[bool] = mapped_column(
        sa.Boolean,
        default=False,
        server_default=sa.false(),
        nullable=False,
    )

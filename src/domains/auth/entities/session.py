from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Self
from uuid import UUID, uuid4


def as_utc(value: datetime) -> datetime:
    """Приводит дату к UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


@dataclass
class Session:
    """Серверная сессия, привязанная к JWT через `jti`."""

    id: UUID
    user_id: int
    created_at: datetime
    expires_at: datetime
    ip_address: str | None = None
    user_agent: str | None = None
    revoked_at: datetime | None = None

    @classmethod
    def create(
        cls,
        user_id: int,
        expires_at: datetime,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
        now: datetime | None = None,
    ) -> Self:
        """Создаёт новую сессию с UUID и временем жизни."""
        return cls(
            id=uuid4(),
            user_id=user_id,
            created_at=now or datetime.now(UTC),
            expires_at=as_utc(expires_at),
            ip_address=ip_address,
            user_agent=user_agent[:512] if user_agent else None,
        )

    @property
    def is_revoked(self) -> bool:
        """Возвращает True, если сессия была отозвана."""
        return self.revoked_at is not None

    def is_valid(self, now: datetime | None = None) -> bool:
        """Проверяет, что сессия не отозвана и не истекла."""
        current = as_utc(now or datetime.now(UTC))
        return not self.is_revoked and current < as_utc(self.expires_at)

    def revoke(self, now: datetime | None = None) -> None:
        """Помечает сессию отозванной."""
        self.revoked_at = as_utc(now or datetime.now(UTC))

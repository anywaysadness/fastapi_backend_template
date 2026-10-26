from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Self
from uuid import UUID, uuid4


def _as_utc(value: datetime) -> datetime:
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
            expires_at=_as_utc(expires_at),
            ip_address=ip_address,
            user_agent=user_agent[:512] if user_agent else None,
        )

    @property
    def is_revoked(self) -> bool:
        """Возвращает True, если сессия была отозвана."""
        return self.revoked_at is not None

    def is_valid(self, now: datetime | None = None) -> bool:
        """Проверяет, что сессия не отозвана и не истекла."""
        current = _as_utc(now or datetime.now(UTC))
        return not self.is_revoked and current < _as_utc(self.expires_at)

    def revoke(self, now: datetime | None = None) -> None:
        """Помечает сессию отозванной."""
        self.revoked_at = _as_utc(now or datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Сериализует сессию для хранения в Redis."""
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Восстанавливает сессию из данных Redis."""
        revoked_at = data.get("revoked_at")
        return cls(
            id=UUID(str(data["id"])),
            user_id=int(data["user_id"]),
            created_at=_as_utc(datetime.fromisoformat(str(data["created_at"]))),
            expires_at=_as_utc(datetime.fromisoformat(str(data["expires_at"]))),
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
            revoked_at=_as_utc(datetime.fromisoformat(str(revoked_at))) if revoked_at else None,
        )

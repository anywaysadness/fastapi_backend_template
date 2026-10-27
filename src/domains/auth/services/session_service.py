from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from src.domains.auth.entities.session import Session, as_utc
from src.domains.auth.interfaces import SessionRepository


class SessionService:
    """Сервис сессий: ходит в репозиторий и преобразует инфраструктурные данные."""

    def __init__(self, repository: SessionRepository) -> None:
        """Сохраняет репозиторий сессий."""
        self._repository = repository

    async def save(self, session: Session) -> None:
        """Сохраняет доменную сессию через репозиторий."""
        ttl_seconds = max(1, int((session.expires_at - datetime.now(UTC)).total_seconds()))
        await self._repository.save(self.to_persistence(session), ttl_seconds)

    async def get_by_id(self, session_id: UUID) -> Session | None:
        """Возвращает валидную доменную сессию по идентификатору."""
        data = await self._repository.get_by_id(session_id)
        if data is None:
            return None

        session = self.to_entity(data)
        if not session.is_valid():
            await self._repository.revoke_by_id(session_id)
            return None

        return session

    async def revoke_by_id(self, session_id: UUID) -> None:
        """Отзывает сессию через репозиторий."""
        await self._repository.revoke_by_id(session_id)

    async def revoke_by_user_id(self, user_id: int) -> int:
        """Отзывает все сессии пользователя через репозиторий."""
        return await self._repository.revoke_by_user_id(user_id)

    def to_entity(self, data: Mapping[str, Any]) -> Session:
        """Восстанавливает доменную сессию из инфраструктурных данных."""
        revoked_at = data.get("revoked_at")
        return Session(
            id=UUID(str(data["id"])),
            user_id=int(data["user_id"]),
            created_at=as_utc(datetime.fromisoformat(str(data["created_at"]))),
            expires_at=as_utc(datetime.fromisoformat(str(data["expires_at"]))),
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
            revoked_at=as_utc(datetime.fromisoformat(str(revoked_at))) if revoked_at else None,
        )

    def to_persistence(self, session: Session) -> dict[str, Any]:
        """Возвращает инфраструктурное представление сессии для репозитория."""
        return {
            "id": str(session.id),
            "user_id": session.user_id,
            "created_at": session.created_at.isoformat(),
            "expires_at": session.expires_at.isoformat(),
            "ip_address": session.ip_address,
            "user_agent": session.user_agent,
            "revoked_at": session.revoked_at.isoformat() if session.revoked_at else None,
        }

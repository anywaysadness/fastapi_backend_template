from typing import Any, Protocol
from uuid import UUID


class SessionRepository(Protocol):
    """Порт хранения серверных сессий в виде инфраструктурных данных."""

    async def save(self, session_data: dict[str, Any], ttl_seconds: int) -> None:
        """Сохраняет сериализованную сессию с TTL."""
        ...

    async def get_by_id(self, session_id: UUID) -> dict[str, Any] | None:
        """Возвращает сериализованную сессию по идентификатору."""
        ...

    async def revoke_by_id(self, session_id: UUID) -> None:
        """Отзывает одну сессию."""
        ...

    async def revoke_by_user_id(self, user_id: int) -> int:
        """Отзывает все сессии пользователя и возвращает их количество."""
        ...

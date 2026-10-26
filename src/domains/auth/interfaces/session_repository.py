from typing import Protocol
from uuid import UUID

from src.domains.auth.entities.session import Session


class SessionRepository(Protocol):
    """Порт хранения серверных сессий."""

    async def save(self, session: Session) -> None:
        """Сохраняет сессию с TTL."""
        ...

    async def get_by_id(self, session_id: UUID) -> Session | None:
        """Возвращает сессию по идентификатору."""
        ...

    async def revoke_by_id(self, session_id: UUID) -> None:
        """Отзывает одну сессию."""
        ...

    async def revoke_by_user_id(self, user_id: int) -> int:
        """Отзывает все сессии пользователя и возвращает их количество."""
        ...

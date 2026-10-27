from collections.abc import Sequence
from datetime import datetime
from typing import Any, Protocol

from src.domains.users.value_objects import UsernameVO


class UserRecord(Protocol):
    """Структурное представление строки БД с пользователем."""

    id: int
    username: str
    hashed_password: str
    email: str | None
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_admin: bool


class UserRepositoryProtocol(Protocol):
    """Порт хранения пользователей, возвращающий инфраструктурные записи."""

    async def get_by_id(self, user_id: int) -> UserRecord | None:
        """Возвращает запись пользователя по идентификатору."""
        ...

    async def find_by_username(self, username: UsernameVO) -> UserRecord | None:
        """Возвращает запись пользователя по username."""
        ...

    async def find_all(self, limit: int = 100, offset: int = 0) -> Sequence[UserRecord]:
        """Возвращает страницу записей пользователей."""
        ...

    async def create(self, data: dict[str, Any]) -> UserRecord:
        """Создаёт запись пользователя из persistence-данных."""
        ...

    async def update(self, user_id: int, data: dict[str, Any]) -> UserRecord:
        """Обновляет запись пользователя persistence-данными."""
        ...

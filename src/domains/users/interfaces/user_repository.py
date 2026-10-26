from collections.abc import Sequence
from typing import Protocol

from src.domains.users.entities import UserEntity
from src.domains.users.value_objects import UsernameVO


class UserRepositoryProtocol(Protocol):
    """Порт хранения пользователей."""

    async def save(self, user: UserEntity) -> UserEntity:
        """Создаёт или обновляет пользователя."""
        ...

    async def get_by_id(self, user_id: int) -> UserEntity | None:
        """Возвращает пользователя по идентификатору."""
        ...

    async def find_by_username(self, username: UsernameVO) -> UserEntity | None:
        """Возвращает пользователя по username."""
        ...

    async def find_all(self, limit: int = 100, offset: int = 0) -> Sequence[UserEntity]:
        """Возвращает страницу пользователей."""
        ...

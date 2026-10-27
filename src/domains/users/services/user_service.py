from collections.abc import Sequence
from typing import Any

from src.domains.uow import UnitOfWork
from src.domains.users.entities import UserEntity
from src.domains.users.interfaces import UserRecord
from src.domains.users.value_objects import EmailVO, UsernameVO


class UserService:
    """Сервис пользователей: ходит в репозиторий и преобразует модели."""

    def __init__(self, uow: UnitOfWork) -> None:
        """Сохраняет Unit of Work для доступа к репозиторию."""
        self._uow = uow

    async def get_by_id(self, user_id: int) -> UserEntity | None:
        """Возвращает доменного пользователя по идентификатору."""
        row = await self._uow.users.get_by_id(user_id)
        return self.to_entity(row) if row is not None else None

    async def find_by_username(self, username: UsernameVO) -> UserEntity | None:
        """Возвращает доменного пользователя по username."""
        row = await self._uow.users.find_by_username(username)
        return self.to_entity(row) if row is not None else None

    async def find_all(self, limit: int = 100, offset: int = 0) -> Sequence[UserEntity]:
        """Возвращает страницу доменных пользователей."""
        rows = await self._uow.users.find_all(limit=limit, offset=offset)
        return [self.to_entity(row) for row in rows]

    async def save(self, user: UserEntity) -> UserEntity:
        """Сохраняет пользователя через репозиторий и возвращает доменную модель."""
        data = self.to_persistence(user)

        if user.is_new:
            data.pop("id", None)
            data.pop("updated_at", None)
            row = await self._uow.users.create(data)
        else:
            if user.id is None:
                raise RuntimeError("Existing user must have an id")
            data.pop("created_at", None)
            row = await self._uow.users.update(user.id, data)

        return self.to_entity(row)

    def to_entity(self, row: UserRecord) -> UserEntity:
        """Восстанавливает доменного пользователя из инфраструктурной записи."""
        email = EmailVO(row.email) if row.email is not None else None
        return UserEntity(
            id=row.id,
            username=UsernameVO(row.username),
            hashed_password=row.hashed_password,
            created_at=row.created_at,
            updated_at=row.updated_at,
            email=email,
            is_active=row.is_active,
            is_admin=row.is_admin,
        )

    def to_persistence(self, user: UserEntity) -> dict[str, Any]:
        """Возвращает persistence-представление пользователя для репозитория."""
        return {
            "id": user.id,
            "username": user.username.value,
            "hashed_password": user.hashed_password,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "email": user.email.value if user.email else None,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
        }

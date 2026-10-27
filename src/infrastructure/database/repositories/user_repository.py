from collections.abc import Sequence
from typing import Any

from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.auth.exceptions import UserAlreadyExistsException
from src.domains.users.interfaces import UserRepositoryProtocol
from src.domains.users.value_objects import UsernameVO
from src.infrastructure.database.models.user import UserModel


class UserRepository(UserRepositoryProtocol):
    """SQLAlchemy-реализация репозитория пользователей.

    Репозиторий только читает и пишет строки БД и не преобразует их
    в доменные сущности: этим занимается ``UserService``.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Привязывает репозиторий к транзакционной сессии."""
        self._session = session

    @property
    def session(self) -> AsyncSession:
        """Возвращает текущую сессию SQLAlchemy."""
        return self._session

    async def get_by_id(self, user_id: int) -> UserModel | None:
        """Возвращает строку пользователя по идентификатору."""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_username(self, username: UsernameVO) -> UserModel | None:
        """Возвращает строку пользователя по нормализованному username."""
        stmt = select(UserModel).where(UserModel.username == username.value)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_all(self, limit: int = 100, offset: int = 0) -> Sequence[UserModel]:
        """Возвращает страницу строк пользователей."""
        stmt = select(UserModel).order_by(UserModel.id).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create(self, data: dict[str, Any]) -> UserModel:
        """Вставляет строку пользователя и возвращает её из БД."""
        stmt = insert(UserModel).values(**data).returning(UserModel)
        try:
            result = await self._session.execute(stmt)
        except IntegrityError as exc:
            raise UserAlreadyExistsException(username=str(data.get("username", ""))) from exc
        return result.scalar_one()

    async def update(self, user_id: int, data: dict[str, Any]) -> UserModel:
        """Обновляет строку пользователя и возвращает её из БД."""
        stmt = update(UserModel).where(UserModel.id == user_id).values(**data).returning(UserModel)
        try:
            result = await self._session.execute(stmt)
        except IntegrityError as exc:
            raise UserAlreadyExistsException(username=str(data.get("username", ""))) from exc
        return result.scalar_one()

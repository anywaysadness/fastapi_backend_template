import logging
from collections.abc import Callable
from typing import Any, Self, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.users.interfaces.user_repository import UserRepositoryProtocol
from src.infrastructure.database.base_repository import SQLAlchemyRepository
from src.infrastructure.database.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

R = TypeVar("R", bound="SQLAlchemyRepository")


class SqlAlchemyUnitOfWork:
    def __init__(
        self,
        session_factory: Callable[[], AsyncSession],
    ) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._cache: dict[str, Any] = {}

    async def __aenter__(self) -> Self:
        if self._session is not None:
            raise RuntimeError("UoW уже запущен")
        self._session = self._session_factory()
        self._cache = {}
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            if exc_type is None:
                await self.commit()
            else:
                await self.rollback()
        finally:
            if self._session is not None:
                await self._session.close()
            self._session = None
            self._cache.clear()

    async def commit(self) -> None:
        if self._session:
            await self._session.commit()

    async def rollback(self) -> None:
        if self._session:
            await self._session.rollback()

    def _get_repo(self, key: str, factory: type[R]) -> R:
        if key not in self._cache:
            self._cache[key] = factory(self._session)
        return self._cache[key]

    @property
    def users(self) -> UserRepositoryProtocol:
        if self._session is None:
            raise RuntimeError("Сессия не инициализирована")
        return self._get_repo("users_repo", UserRepository)

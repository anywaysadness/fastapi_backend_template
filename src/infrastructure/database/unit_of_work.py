from collections.abc import Callable
from typing import Any, Self, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.domains.users.interfaces import UserRepositoryProtocol
from src.infrastructure.database.connection import async_session_maker
from src.infrastructure.database.repositories.user_repository import UserRepository

R = TypeVar("R")


class SqlAlchemyUnitOfWork:
    """SQLAlchemy Unit of Work с кэшем репозиториев."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession] | None = None,
    ) -> None:
        """Сохраняет фабрику сессий для текущей транзакции."""
        self._session_factory = session_factory or async_session_maker
        self._session: AsyncSession | None = None
        self._cache: dict[str, Any] = {}

    async def __aenter__(self) -> Self:
        """Открывает новую сессию SQLAlchemy."""
        if self._session is not None:
            raise RuntimeError("UoW уже запущен")
        self._session = self._session_factory()
        self._cache = {}
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Фиксирует транзакцию или откатывает её при ошибке."""
        try:
            if exc_type is not None:
                await self.rollback()
            else:
                await self.commit()
        finally:
            if self._session is not None:
                await self._session.close()
            self._session = None
            self._cache.clear()

    async def commit(self) -> None:
        """Фиксирует текущую транзакцию."""
        if self._session is not None:
            await self._session.commit()

    async def rollback(self) -> None:
        """Откатывает текущую транзакцию."""
        if self._session is not None:
            await self._session.rollback()

    def _get_repo(self, key: str, factory: Callable[[AsyncSession], R]) -> R:
        """Возвращает репозиторий из кэша или создаёт его."""
        if key not in self._cache:
            if self._session is None:
                raise RuntimeError("Сессия не инициализирована")
            repository = factory(self._session)
            self._cache[key] = repository
        return self._cache[key]

    @property
    def users(self) -> UserRepositoryProtocol:
        """Возвращает репозиторий пользователей."""
        return self._get_repo("users_repo", UserRepository)

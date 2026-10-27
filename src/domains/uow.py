from types import TracebackType
from typing import Protocol, Self

from src.domains.users.interfaces import UserRepositoryProtocol


class UnitOfWork(Protocol):
    """Порт транзакции и доступа к инфраструктурным репозиториям."""

    @property
    def users(self) -> UserRepositoryProtocol:
        """Возвращает репозиторий пользователей."""
        ...

    async def __aenter__(self) -> Self:
        """Открывает транзакционный контекст."""
        ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Фиксирует транзакцию или откатывает её при ошибке."""
        ...

    async def commit(self) -> None:
        """Фиксирует текущую транзакцию."""
        ...

    async def rollback(self) -> None:
        """Откатывает текущую транзакцию."""
        ...

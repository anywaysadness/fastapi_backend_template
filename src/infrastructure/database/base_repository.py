from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Generic, Protocol, TypeVar

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.connection import async_session_maker


class HasId(Protocol):
    id: int


T = TypeVar("T", bound=HasId)


class AbstractRepository(ABC, Generic[T]):
    @abstractmethod
    async def create_one(self, data: dict) -> T:
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, id: int) -> T | None:
        raise NotImplementedError

    @abstractmethod
    async def find_all(self) -> Sequence[T]:
        raise NotImplementedError

    @abstractmethod
    async def update_one(self, id: int, data: dict) -> T:
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, id: int) -> None:
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository[T], Generic[T]):
    model: type[T]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @property
    def session(self) -> AsyncSession:
        return self._session

    async def create_one(self, data: dict) -> T:
        stmt = insert(self.model).values(**data).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def find_one(self, id: int) -> T | None:
        stmt = select(self.model).where(self.model.id == id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def find_all(self) -> Sequence[T]:
        stmt = select(self.model)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def update_one(self, id: int, data: dict) -> T:
        stmt = update(self.model).where(self.model.id == id).values(**data).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def delete_one(self, id: int) -> None:
        stmt = delete(self.model).where(self.model.id == id)
        await self.session.execute(stmt)

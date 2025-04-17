from abc import ABC, abstractmethod
from typing import Generic, Protocol, TypeVar

from sqlalchemy import delete, insert, select, update

from src.core.db_session import async_session_maker


class HasId(Protocol):
    id: int


T = TypeVar("T", bound=HasId)


class AbstractRepository(ABC, Generic[T]):
    @abstractmethod
    async def create_one(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, id: int):
        raise NotImplementedError

    @abstractmethod
    async def find_all(self):
        raise NotImplementedError

    @abstractmethod
    async def update_one(self, id: int, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, id: int):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository[T]):
    model: type[T]

    async def create_one(self, data: dict) -> int:
        async with async_session_maker() as session:
            stmt = insert(self.model).values(**data).returning(self.model)
            res = await session.execute(stmt)
            await session.commit()
            return res.scalar_one()

    async def find_one(self, id: int):
        async with async_session_maker() as session:
            stmt = select(self.model).where(self.model.id == id)
            res = await session.execute(stmt)
            return res.scalar_one_or_none()

    async def find_all(self):
        async with async_session_maker() as session:
            stmt = select(self.model)
            res = await session.execute(stmt)
            return res.scalars().all()

    async def update_one(self, id: int, data: dict):
        async with async_session_maker() as session:
            stmt = update(self.model).where(self.model.id == id).values(**data).returning(self.model)
            res = await session.execute(stmt)
            await session.commit()
            return res.scalar_one()

    async def delete_one(self, id: int):
        async with async_session_maker() as session:
            stmt = delete(self.model).where(self.model.id == id)
            res = await session.execute(stmt)
            await session.commit()

            if res.rowcount == 0:
                raise Exception

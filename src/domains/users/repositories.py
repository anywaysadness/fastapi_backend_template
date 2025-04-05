from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import joinedload, selectinload

from src.core.base_repository import SQLAlchemyRepository
from src.core.db_session import async_session_maker
from src.domains.users.models import User


class UserRepository(SQLAlchemyRepository):
    model: type[User] = User

    async def find_by_login(self, login: str):
        async with async_session_maker() as session:
            stmt = select(self.model).where(self.model.login == login)
            res = await session.execute(stmt)
            return res.scalar_one_or_none()

    async def find_one(self, id: int):
        async with async_session_maker() as session:
            stmt = select(self.model).where(self.model.id == id)
            res = await session.execute(stmt)
            return res.scalar_one()

    async def update_one(self, id: int, data: dict):
        async with async_session_maker() as session:
            stmt = update(self.model).where(self.model.id == id).values(data).returning(self.model)
            res = await session.execute(stmt)
            await session.commit()
            return res.scalar_one()

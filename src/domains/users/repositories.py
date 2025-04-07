from sqlalchemy import select

from src.core.base_repository import SQLAlchemyRepository
from src.core.db_session import async_session_maker
from src.domains.users.models import User


class UserRepository(SQLAlchemyRepository):
    model: type[User] = User

    async def find_by_username(self, username: str):
        async with async_session_maker() as session:
            stmt = select(self.model).where(self.model.username == username)
            res = await session.execute(stmt)
            return res.scalar_one_or_none()

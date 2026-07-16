from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.auth.value_objects import UsernameVO
from src.domains.users.entities import UserEntity
from src.infrastructure.database.base_repository import SQLAlchemyRepository
from src.infrastructure.database.connection import async_session_maker
from src.infrastructure.database.models.user import UserModel


class UserRepository(SQLAlchemyRepository[UserModel]):
    model: type[UserModel] = UserModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_one(self, user_id: int) -> UserEntity | None:
        stmt = select(self.model).where(self.model.id == user_id)
        res = await self.session.execute(stmt)
        row = res.scalar_one_or_none()

        return self._model_to_entity(row)

    async def save(self, user: UserEntity) -> UserEntity:
        data = user.to_dict()
        data.pop("id", None)

        if user.id == 0:
            # create
            created_model = await self.create_one(data)
            return self._model_to_entity(created_model)

        # update
        data.pop("created_at", None)

        updated_model = await self.update_one(user.id, data)
        return self._model_to_entity(updated_model)

    async def find_by_username(self, username: UsernameVO) -> UserEntity | None:
        stmt = select(self.model).where(self.model.username == username.value)
        res = await self.session.execute(stmt)
        row = res.scalar_one_or_none()

        return self._model_to_entity(row)

    def _model_to_entity(self, row: UserModel | None) -> UserEntity | None:
        if row is None:
            return None

        data = {
            "id": row.id,
            "username": row.username,
            "hashed_password": row.hashed_password,
            "email": row.email,
            "created_at": row.created_at,
            "is_active": row.is_active,
            "is_admin": row.is_admin,
        }

        return UserEntity.from_dict(data)

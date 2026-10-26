from collections.abc import Sequence

from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.auth.exceptions import UserAlreadyExistsException
from src.domains.users.entities import UserEntity
from src.domains.users.value_objects import UsernameVO
from src.infrastructure.database.models.user import UserModel


class UserRepository:
    """SQLAlchemy-реализация репозитория пользователей."""

    def __init__(self, session: AsyncSession) -> None:
        """Привязывает репозиторий к транзакционной сессии."""
        self._session = session

    @property
    def session(self) -> AsyncSession:
        """Возвращает текущую сессию SQLAlchemy."""
        return self._session

    async def get_by_id(self, user_id: int) -> UserEntity | None:
        """Возвращает пользователя по идентификатору."""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        return self._model_to_entity(result.scalar_one_or_none())

    async def save(self, user: UserEntity) -> UserEntity:
        """Создаёт или обновляет пользователя."""
        data = user.to_persistence()
        data.pop("id", None)
        self._session.info["uow_dirty"] = True

        try:
            if user.is_new:
                data.pop("updated_at", None)
                created_model = await self._create(data)
                created = self._model_to_entity(created_model)
                if created is None:
                    raise RuntimeError("Created user could not be mapped")
                return created

            if user.id is None:
                raise RuntimeError("Existing user must have an id")

            data.pop("created_at", None)
            updated_model = await self._update(user.id, data)
            updated = self._model_to_entity(updated_model)
            if updated is None:
                raise RuntimeError("Updated user could not be mapped")
            return updated
        except IntegrityError as exc:
            raise UserAlreadyExistsException(username=user.username.value) from exc

    async def find_by_username(self, username: UsernameVO) -> UserEntity | None:
        """Возвращает пользователя по нормализованному username."""
        stmt = select(UserModel).where(UserModel.username == username.value)
        result = await self._session.execute(stmt)
        return self._model_to_entity(result.scalar_one_or_none())

    async def find_all(self, limit: int = 100, offset: int = 0) -> Sequence[UserEntity]:
        """Возвращает страницу пользователей."""
        stmt = select(UserModel).order_by(UserModel.id).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        entities: list[UserEntity] = []
        for row in result.scalars().all():
            entity = self._model_to_entity(row)
            if entity is not None:
                entities.append(entity)
        return entities

    async def _create(self, data: dict) -> UserModel:
        """Вставляет пользователя и возвращает строку БД."""
        stmt = insert(UserModel).values(**data).returning(UserModel)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def _update(self, user_id: int, data: dict) -> UserModel:
        """Обновляет пользователя и возвращает строку БД."""
        stmt = update(UserModel).where(UserModel.id == user_id).values(**data).returning(UserModel)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    def _model_to_entity(self, row: UserModel | None) -> UserEntity | None:
        """Преобразует строку БД в доменную сущность."""
        if row is None:
            return None

        return UserEntity.from_dict(
            {
                "id": row.id,
                "username": row.username,
                "hashed_password": row.hashed_password,
                "email": row.email,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
                "is_active": row.is_active,
                "is_admin": row.is_admin,
            }
        )

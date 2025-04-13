import logging

from src.core.exceptions import InvalidCredentialsException
from src.core.jwt_auth import hash_password
from src.domains.users.repositories import UserRepository
from src.domains.users.schemas import BaseUserSchema, UpdateUserSchema, UserSchema

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository: UserRepository = user_repository

    async def register_user(self, user_data: BaseUserSchema) -> UserSchema:
        """Регистрация нового пользователя"""
        user = await self.user_repository.find_by_username(user_data.username)
        if user is not None:
            raise InvalidCredentialsException
        
        user_data_dict = user_data.model_dump(exclude="password")
        user_data_dict["hashed_password"] = hash_password(user_data.password)
        
        created_user = await self.user_repository.create_one(user_data_dict)
        return UserSchema.model_validate(created_user)

    async def update_user(self, id: int, user_data: UpdateUserSchema) -> UserSchema:
        """Обновление информации юзера"""
        user_data_dict = user_data.model_dump()

        if user_data.password:
            hashed_password = hash_password(user_data.password)
            user_data_dict["hashed_password"] = hashed_password

        updated_user = await self.user_repository.update_one(id, user_data_dict)

        return UserSchema.model_validate(updated_user)

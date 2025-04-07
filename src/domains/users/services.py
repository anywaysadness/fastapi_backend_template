from src.core.exceptions import UserAlreadyExistsException, UserNotFoundException
from src.core.jwt_auth import get_password_hash
from src.domains.users.repositories import UserRepository
from src.domains.users.schemas import CreateUserSchema, UpdateUserSchema, UserSchema


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository: UserRepository = user_repository

    async def register_user(self, user_data: CreateUserSchema) -> UserSchema:
        """Регистрация нового пользователя"""
        user = await self.user_repository.find_by_username(user_data.username)
        if user is not None:
            raise UserAlreadyExistsException
        hashed_password = get_password_hash(user_data.password)
        user_data_dict = user_data.model_dump()
        user_data_dict["hashed_password"] = hashed_password

        created_user = await self.user_repository.create_one(user_data_dict)

        return UserSchema.model_validate(created_user)

    async def get_user(self, id: int) -> UserSchema:
        """Получение юзера по id"""
        user = await self.user_repository.find_one(id)
        if user is None:
            raise UserNotFoundException
        return UserSchema.model_validate(user)

    async def update_user(self, id: int, user_data: UpdateUserSchema) -> UserSchema:
        """Обновление информации юзера"""
        user_data_dict = user_data.model_dump()

        if user_data.password:
            hashed_password = get_password_hash(user_data.password)
            user_data_dict["hashed_password"] = hashed_password

        updated_user = await self.user_repository.update_one(id, user_data_dict)

        return UserSchema.model_validate(updated_user)

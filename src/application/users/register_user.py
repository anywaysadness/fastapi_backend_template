from collections.abc import Callable

from src.domains.auth.exceptions import UserAlreadyExistsException
from src.domains.auth.password_service import PasswordService
from src.domains.auth.value_objects import PasswordVO, UsernameVO
from src.domains.users.entities import UserEntity
from src.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from src.presentation.user.schemas import BaseUserSchema


class UserRegistrationUseCase:
    def __init__(self, session_factory: Callable, password_service: PasswordService) -> None:
        self._session_factory = session_factory
        self._password_service = password_service

    async def user_registration(self, data: BaseUserSchema) -> UserEntity:
        print(f"DEBUG IN USECASE: {type(self._session_factory)}")
        username = UsernameVO(data.username)
        password = PasswordVO(data.password)

        async with SqlAlchemyUnitOfWork(self._session_factory) as uow:
            existing = await uow.users.find_by_username(username)
            if existing is not None:
                raise UserAlreadyExistsException(username=username.value)

            hashed = self._password_service.hash(password.value)
            user = UserEntity.create(username=username, hashed_password=hashed)
            saved = await uow.users.save(user)
        return saved

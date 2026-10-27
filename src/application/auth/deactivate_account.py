from src.domains.auth.auth_service import AuthService
from src.domains.auth.exceptions import UserNotFoundException
from src.domains.auth.services import SessionService
from src.domains.auth.value_objects import PasswordVO
from src.domains.uow import UnitOfWork
from src.domains.users.entities import UserEntity
from src.domains.users.services import UserService


class DeactivateAccountUseCase:
    """Сценарий деактивации аккаунта."""

    def __init__(
        self,
        uow: UnitOfWork,
        auth_service: AuthService,
        user_service: UserService,
        session_service: SessionService,
    ) -> None:
        """Сохраняет зависимости сценария."""
        self._uow = uow
        self._auth_service = auth_service
        self._user_service = user_service
        self._session_service = session_service

    async def execute(self, user_id: int, password: str) -> UserEntity:
        """Проверяет пароль, деактивирует пользователя и отзывает сессии."""
        password_vo = PasswordVO(password)

        async with self._uow:
            user = await self._user_service.get_by_id(user_id)
            if user is None:
                raise UserNotFoundException(username=str(user_id))

            user = self._auth_service.verify_credentials(user, password_vo)
            user.deactivate()
            user = await self._user_service.save(user)
            await self._session_service.revoke_by_user_id(user_id)

        return user

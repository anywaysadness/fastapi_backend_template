from src.application.common.uow import UnitOfWork
from src.domains.auth.auth_service import AuthService
from src.domains.auth.exceptions import UserNotFoundException
from src.domains.auth.interfaces import SessionRepository
from src.domains.auth.value_objects import PasswordVO
from src.domains.users.entities import UserEntity


class DeactivateAccountUseCase:
    """Сценарий деактивации аккаунта."""

    def __init__(
        self,
        uow: UnitOfWork,
        auth_service: AuthService,
        session_repository: SessionRepository,
    ) -> None:
        """Сохраняет зависимости сценария."""
        self._uow = uow
        self._auth_service = auth_service
        self._session_repository = session_repository

    async def execute(self, user_id: int, password: str) -> UserEntity:
        """Проверяет пароль, деактивирует пользователя и отзывает сессии."""
        password_vo = PasswordVO(password)

        async with self._uow:
            user = await self._uow.users.get_by_id(user_id)
            if user is None:
                raise UserNotFoundException(username=str(user_id))

            user = self._auth_service.verify_credentials(user, password_vo)
            user.deactivate()
            user = await self._uow.users.save(user)
            await self._session_repository.revoke_by_user_id(user_id)

        return user

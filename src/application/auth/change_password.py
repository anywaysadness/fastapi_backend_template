from src.common.password_policy import missing_password_requirements
from src.domains.auth.auth_service import AuthService
from src.domains.auth.exceptions import UserNotFoundException, WeakPasswordError
from src.domains.auth.interfaces import PasswordHasher
from src.domains.auth.services import SessionService
from src.domains.auth.value_objects import PasswordVO
from src.domains.uow import UnitOfWork
from src.domains.users.services import UserService


class ChangePasswordUseCase:
    """Сценарий смены пароля."""

    def __init__(
        self,
        uow: UnitOfWork,
        auth_service: AuthService,
        password_hasher: PasswordHasher,
        user_service: UserService,
        session_service: SessionService,
    ) -> None:
        """Сохраняет зависимости сценария."""
        self._uow = uow
        self._auth_service = auth_service
        self._password_hasher = password_hasher
        self._user_service = user_service
        self._session_service = session_service

    async def execute(self, user_id: int, current_password: str, new_password: str) -> None:
        """Меняет пароль и отзывает все сессии пользователя."""
        current = PasswordVO(current_password)
        new = PasswordVO(new_password)
        if missing_password_requirements(new.value):
            raise WeakPasswordError()

        async with self._uow:
            user = await self._user_service.get_by_id(user_id)
            if user is None:
                raise UserNotFoundException(username=str(user_id))

            user = self._auth_service.verify_credentials(user, current)
            user.change_password(self._password_hasher.hash(new.value))
            await self._user_service.save(user)
            await self._session_service.revoke_by_user_id(user_id)

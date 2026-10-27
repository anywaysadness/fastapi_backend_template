from src.application.common.exceptions import RateLimitExceededError
from src.application.common.rate_limiter import RateLimiter
from src.application.users.dto import RegisterUserCommand
from src.common.password_policy import missing_password_requirements
from src.domains.auth.exceptions import UserAlreadyExistsException, WeakPasswordError
from src.domains.auth.interfaces import PasswordHasher
from src.domains.auth.value_objects import PasswordVO, UsernameVO
from src.domains.uow import UnitOfWork
from src.domains.users.entities import UserEntity
from src.domains.users.services import UserService


class RegisterUserUseCase:
    """Сценарий регистрации пользователя."""

    def __init__(
        self,
        uow: UnitOfWork,
        user_service: UserService,
        password_hasher: PasswordHasher,
        rate_limiter: RateLimiter,
        max_attempts: int,
        window_seconds: int,
    ) -> None:
        """Сохраняет зависимости сценария."""
        self._uow = uow
        self._user_service = user_service
        self._password_hasher = password_hasher
        self._rate_limiter = rate_limiter
        self._max_attempts = max_attempts
        self._window_seconds = window_seconds

    async def execute(self, command: RegisterUserCommand) -> UserEntity:
        """Создаёт пользователя с Argon2-хешем и проверяет уникальность username."""
        username = UsernameVO(command.username)
        password = PasswordVO(command.password)
        if missing_password_requirements(password.value):
            raise WeakPasswordError()

        allowed = await self._rate_limiter.allow(
            scope="register",
            identity=f"{command.ip_address or 'unknown'}:{username.value}",
            limit=self._max_attempts,
            window_seconds=self._window_seconds,
        )
        if not allowed:
            raise RateLimitExceededError()

        hashed_password = self._password_hasher.hash(password.value)
        async with self._uow:
            existing = await self._user_service.find_by_username(username)
            if existing is not None:
                raise UserAlreadyExistsException(username=username.value)

            user = UserEntity.create(username=username, hashed_password=hashed_password)
            return await self._user_service.save(user)

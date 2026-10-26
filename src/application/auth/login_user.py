from datetime import UTC, datetime, timedelta
from uuid import UUID

from src.application.auth.dto import LoginCommand, LoginResult
from src.application.common.exceptions import RateLimitExceededError
from src.application.common.rate_limiter import RateLimiter
from src.application.common.uow import UnitOfWork
from src.domains.auth.auth_service import AuthService
from src.domains.auth.entities import Session
from src.domains.auth.interfaces import SessionRepository, TokenService
from src.domains.auth.value_objects import PasswordVO, UsernameVO


class LoginUserUseCase:
    """Сценарий входа пользователя."""

    def __init__(
        self,
        uow: UnitOfWork,
        auth_service: AuthService,
        token_service: TokenService,
        session_repository: SessionRepository,
        rate_limiter: RateLimiter,
        max_attempts: int,
        window_seconds: int,
    ) -> None:
        """Сохраняет зависимости сценария."""
        self._uow = uow
        self._auth_service = auth_service
        self._token_service = token_service
        self._session_repository = session_repository
        self._rate_limiter = rate_limiter
        self._max_attempts = max_attempts
        self._window_seconds = window_seconds

    async def execute(self, command: LoginCommand) -> LoginResult:
        """Проверяет лимит и учётные данные, создаёт сессию и access-токен."""
        username = UsernameVO(command.username)
        password = PasswordVO(command.password)

        allowed = await self._rate_limiter.allow(
            scope="login",
            identity=f"{command.ip_address or 'unknown'}:{username.value}",
            limit=self._max_attempts,
            window_seconds=self._window_seconds,
        )
        if not allowed:
            raise RateLimitExceededError()

        async with self._uow:
            user = await self._uow.users.find_by_username(username)

        user = self._auth_service.verify_credentials(user, password)
        if user.id is None:
            raise RuntimeError("Authenticated user must have an id")

        expires_in = self._token_service.access_token_ttl_seconds
        session = Session.create(
            user_id=user.id,
            expires_at=datetime.now(UTC) + timedelta(seconds=expires_in),
            ip_address=command.ip_address,
            user_agent=command.user_agent,
        )
        await self._session_repository.save(session)

        access_token = self._token_service.create_access_token(user.id, session.id)
        return LoginResult(user=user, access_token=access_token, expires_in=expires_in)

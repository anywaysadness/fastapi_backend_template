from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from fastapi.security import APIKeyCookie
from redis.asyncio import Redis

from src.application.auth import (
    ChangePasswordUseCase,
    DeactivateAccountUseCase,
    GetCurrentUserUseCase,
    LoginUserUseCase,
    LogoutUserUseCase,
)
from src.application.common.rate_limiter import RateLimiter
from src.application.common.uow import UnitOfWork
from src.common.configuration import conf
from src.di.common import get_rate_limiter, get_redis_client, get_uow
from src.domains.auth.auth_service import AuthService
from src.domains.auth.exceptions import ForbiddenError, NotAuthorizedError
from src.domains.auth.interfaces import PasswordHasher, SessionRepository, TokenService
from src.domains.users.entities import UserEntity
from src.infrastructure.auth import Argon2PasswordHasher, JwtService, RedisSessionRepository

auth_cookie_scheme = APIKeyCookie(
    name=conf.app.AUTH_COOKIE_NAME,
    scheme_name="AuthCookie",
    description="HttpOnly cookie с access-JWT, устанавливается при входе.",
    auto_error=False,
)


@lru_cache
def get_password_hasher() -> PasswordHasher:
    """Возвращает singleton-экземпляр Argon2-хешера."""
    return Argon2PasswordHasher(
        pepper=conf.password.PEPPER.get_secret_value(),
        time_cost=conf.password.ARGON2_TIME_COST,
        memory_cost=conf.password.ARGON2_MEMORY_COST,
        parallelism=conf.password.ARGON2_PARALLELISM,
    )


def get_auth_service(
    password_hasher: PasswordHasher = Depends(get_password_hasher),
) -> AuthService:
    """Собирает доменный сервис проверки учётных данных."""
    return AuthService(password_hasher=password_hasher)


@lru_cache
def get_token_service() -> TokenService:
    """Возвращает singleton-экземпляр JWT-сервиса."""
    return JwtService(
        secret_key=conf.jwt_auth.SECRET_KEY.get_secret_value(),
        algorithm=conf.jwt_auth.ALGORITHM,
        expire_minutes=conf.jwt_auth.ACCESS_TOKEN_EXPIRE_MINUTES,
        issuer=conf.jwt_auth.ISSUER,
        audience=conf.jwt_auth.AUDIENCE,
    )


def get_session_repository(redis_client: Redis = Depends(get_redis_client)) -> SessionRepository:
    """Создаёт Redis-репозиторий серверных сессий."""
    return RedisSessionRepository(redis_client)


def get_login_use_case(
    uow: UnitOfWork = Depends(get_uow),
    auth_service: AuthService = Depends(get_auth_service),
    token_service: TokenService = Depends(get_token_service),
    session_repository: SessionRepository = Depends(get_session_repository),
    rate_limiter: RateLimiter = Depends(get_rate_limiter),
) -> LoginUserUseCase:
    """Собирает use case входа."""
    return LoginUserUseCase(
        uow=uow,
        auth_service=auth_service,
        token_service=token_service,
        session_repository=session_repository,
        rate_limiter=rate_limiter,
        max_attempts=conf.rate_limit.LOGIN_ATTEMPTS,
        window_seconds=conf.rate_limit.LOGIN_WINDOW_SECONDS,
    )


def get_logout_use_case(
    token_service: TokenService = Depends(get_token_service),
    session_repository: SessionRepository = Depends(get_session_repository),
) -> LogoutUserUseCase:
    """Собирает use case выхода."""
    return LogoutUserUseCase(
        token_service=token_service,
        session_repository=session_repository,
    )


def get_current_user_use_case(
    uow: UnitOfWork = Depends(get_uow),
    token_service: TokenService = Depends(get_token_service),
    session_repository: SessionRepository = Depends(get_session_repository),
) -> GetCurrentUserUseCase:
    """Собирает use case получения текущего пользователя."""
    return GetCurrentUserUseCase(
        uow=uow,
        token_service=token_service,
        session_repository=session_repository,
    )


async def get_current_user(
    token: Annotated[str | None, Depends(auth_cookie_scheme)],
    use_case: Annotated[GetCurrentUserUseCase, Depends(get_current_user_use_case)],
) -> UserEntity:
    """Извлекает и проверяет access-токен из cookie."""
    if not token:
        raise NotAuthorizedError()
    return await use_case.execute(token)


async def require_admin(
    current_user: Annotated[UserEntity, Depends(get_current_user)],
) -> UserEntity:
    """Пропускает только администратора."""
    if not current_user.is_admin:
        raise ForbiddenError()
    return current_user


def get_change_password_use_case(
    uow: UnitOfWork = Depends(get_uow),
    auth_service: AuthService = Depends(get_auth_service),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    session_repository: SessionRepository = Depends(get_session_repository),
) -> ChangePasswordUseCase:
    """Собирает use case смены пароля."""
    return ChangePasswordUseCase(
        uow=uow,
        auth_service=auth_service,
        password_hasher=password_hasher,
        session_repository=session_repository,
    )


def get_deactivate_account_use_case(
    uow: UnitOfWork = Depends(get_uow),
    auth_service: AuthService = Depends(get_auth_service),
    session_repository: SessionRepository = Depends(get_session_repository),
) -> DeactivateAccountUseCase:
    """Собирает use case деактивации аккаунта."""
    return DeactivateAccountUseCase(
        uow=uow,
        auth_service=auth_service,
        session_repository=session_repository,
    )

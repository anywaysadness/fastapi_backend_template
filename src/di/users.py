from fastapi import Depends

from src.application.common.rate_limiter import RateLimiter
from src.application.users.register_user import RegisterUserUseCase
from src.common.configuration import conf
from src.di.auth import get_password_hasher
from src.di.common import get_rate_limiter, get_uow
from src.di.services import get_user_service
from src.domains.auth.interfaces import PasswordHasher
from src.domains.uow import UnitOfWork
from src.domains.users.services import UserService


def get_register_user_use_case(
    uow: UnitOfWork = Depends(get_uow),
    user_service: UserService = Depends(get_user_service),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    rate_limiter: RateLimiter = Depends(get_rate_limiter),
) -> RegisterUserUseCase:
    """Собирает use case регистрации пользователя."""
    return RegisterUserUseCase(
        uow=uow,
        user_service=user_service,
        password_hasher=password_hasher,
        rate_limiter=rate_limiter,
        max_attempts=conf.rate_limit.REGISTER_ATTEMPTS,
        window_seconds=conf.rate_limit.REGISTER_WINDOW_SECONDS,
    )

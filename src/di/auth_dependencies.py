from functools import lru_cache

from fastapi import Depends

from src.application.users.auth_user import UserAuthUseCase
from src.application.users.register_user import UserRegistrationUseCase
from src.common.configuration import conf
from src.domains.auth.auth_service import AuthService
from src.domains.auth.password_service import PasswordService
from src.infrastructure.auth.jwt_service import JwtService
from src.infrastructure.database.connection import async_session_maker
from src.presentation.user.security import create_cookie_scheme, get_token_payload_dependency


@lru_cache
def get_password_service() -> PasswordService:
    return PasswordService(
        secret_key=conf.token.SECRET_KEY,
        hmac_digest=conf.token.TOKEN_HMAC_DIGEST_MODE,
        encoding=conf.token.TOKEN_DEFAULT_ENCODING,
    )


@lru_cache
def get_auth_service() -> AuthService:
    return AuthService(password_service=get_password_service())


@lru_cache
def get_jwt_service() -> JwtService:
    return JwtService(
        secret_key=conf.jwt_auth.SECRET_KEY,
        algorithm=conf.jwt_auth.ALGORITHM,
    )


access_cookie_scheme = create_cookie_scheme(conf.jwt_auth.ACCESS_TOKEN_TYPE + conf.jwt_auth.COOKIE_KEY)


def get_access_token_payload(
    jwt_service: JwtService = Depends(get_jwt_service),
) -> dict:
    return get_token_payload_dependency(access_cookie_scheme, jwt_service, "access")


def user_auth_use_case(
    auth_service: AuthService = Depends(get_auth_service),
    jwt_service: JwtService = Depends(get_jwt_service),
) -> UserAuthUseCase:
    return UserAuthUseCase(
        session_factory=async_session_maker,
        auth_service=auth_service,
        jwt_service=jwt_service,
    )


def registration_user_use_case(
    password_service: PasswordService = Depends(get_password_service),
) -> UserRegistrationUseCase:
    return UserRegistrationUseCase(
        session_factory=async_session_maker,
        password_service=password_service,
    )

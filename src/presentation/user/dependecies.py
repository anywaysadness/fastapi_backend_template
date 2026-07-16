# src/presentation/auth/dependencies.py
from functools import lru_cache

from fastapi import Depends

from src.common.configuration import conf
from src.domains.auth.password_service import PasswordService
from src.infrastructure.auth.jwt_service import JwtService
from src.presentation.user.security import create_cookie_scheme, get_token_payload_dependency


@lru_cache
def get_password_service() -> PasswordService:
    return PasswordService(
        secret_key=conf.token.SECRET_KEY,
        hmac_digest=conf.token.TOKEN_HMAC_DIGEST_MODE,
        encoding=conf.token.TOKEN_DEFAULT_ENCODING,
    )


@lru_cache
def get_jwt_service() -> JwtService:
    return JwtService(
        secret_key=conf.token.SECRET_KEY,
        algorithm=conf.token.ALGORITHM,
        token_type_field=conf.token.TOKEN_TYPE_FIELD,
    )


access_cookie_scheme = create_cookie_scheme(conf.token.ACCESS_TOKEN_TYPE + conf.token.COOKIE_KEY)


def get_access_token_payload(
    jwt_service: JwtService = Depends(get_jwt_service),
) -> dict:
    return get_token_payload_dependency(access_cookie_scheme, jwt_service, "access")

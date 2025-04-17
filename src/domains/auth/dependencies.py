from fastapi import Depends

from src.core.configuration import conf
from src.core.jwt_auth import get_token_payload_dependency
from src.domains.auth.services import AuthService
from src.domains.users.repositories import UserRepository
from src.domains.users.schemas import UserSchema


def auth_service() -> AuthService:
    return AuthService(UserRepository())


get_access_token_payload = get_token_payload_dependency(conf.jwt_auth.ACCESS_TOKEN_TYPE)
get_refresh_token_payload = get_token_payload_dependency(conf.jwt_auth.REFRESH_TOKEN_TYPE)


async def get_current_user(
    auth_service: AuthService = Depends(auth_service), payload: dict = Depends(get_access_token_payload)
) -> UserSchema:
    return await auth_service.get_current_user(payload)


async def get_current_admin_user(
    auth_service: AuthService = Depends(auth_service), payload: dict = Depends(get_access_token_payload)
) -> UserSchema:
    return await auth_service.get_current_admin_user(payload)


async def get_current_user_by_refresh(
    auth_service: AuthService = Depends(auth_service), payload: dict = Depends(get_refresh_token_payload)
) -> UserSchema:
    return await auth_service.get_current_user(payload)

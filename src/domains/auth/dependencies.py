from typing import Annotated

from fastapi import Depends

from src.domains.auth.services import AuthService
from src.domains.users.models import User
from src.domains.users.repositories import UserRepository


def auth_service():
    return AuthService(UserRepository())


async def get_current_admin_user(
    auth_service: Annotated[AuthService, Depends(auth_service)],
    user: User = Depends(auth_service().get_current_auth_user),
) -> User:
    return await auth_service.get_current_admin_user(user)

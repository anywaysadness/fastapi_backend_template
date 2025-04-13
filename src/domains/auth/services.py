import logging

from fastapi import Depends, HTTPException, Response

from src.core import jwt_auth
from src.core.configuration import conf
from src.core.exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
    UserNotActiveException,
    UserNotAdminException,
)
from src.domains.auth.schemas import TokenInfo
from src.domains.users.models import User
from src.domains.users.repositories import UserRepository
from src.domains.users.schemas import BaseUserSchema

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository: UserRepository = user_repository

    async def get_current_auth_user(self, payload: dict = Depends(jwt_auth.get_current_token_payload)) -> User:
        """Получение текущего юзера"""
        username: str | None = payload.get("sub")
        user = await self.user_repository.find_by_username(username)
        if not user:
            raise InvalidTokenException
        return user

    async def get_current_active_user(self, user: User = Depends(get_current_auth_user)) -> User:
        """Получение текущего юзера как активного"""
        try:
            if not user.is_active:
                raise UserNotActiveException
            return user
        except UserNotActiveException:
            raise
        except Exception as err:
            logger.error(f"Ошибка авторизации: {err}")
            raise HTTPException(status_code=400, detail=f"Ошибка авторизации: {err}")

    async def get_current_admin_user(self, user: User = Depends(get_current_auth_user)) -> User:
        """Получение текущего юзера как админа"""
        try:
            if not user.is_admin:
                raise UserNotAdminException
            return user
        except UserNotAdminException:
            raise
        except Exception as err:
            logger.error(f"Ошибка авторизации: {err}")
            raise HTTPException(status_code=400, detail=f"Ошибка авторизации: {err}")

    @staticmethod
    async def create_access_token(user: User) -> TokenInfo:
        """Создает токен для пользователя"""
        payload = {"sub": user.username, "usesrname": user.username, "email": user.email}
        token = jwt_auth.encode_jwt(payload)
        return TokenInfo(access_token=token, token_type="Bearer")

    async def check_user_exists(self, user_data: BaseUserSchema) -> User:
        """Аутентифицировать юзера"""
        user = await self.user_repository.find_by_username(user_data.username)
        if not user or not jwt_auth.verify_password(user_data.password, user.hashed_password.encode()):
            raise InvalidCredentialsException
        return user

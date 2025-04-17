import logging
from datetime import timedelta

from fastapi import HTTPException
from fastapi.responses import JSONResponse

from src.core import jwt_auth
from src.core.configuration import conf
from src.core.exceptions import (
    InvalidCredentialsException,
    UserDoesNotExist,
    UserNotActiveException,
    UserNotAdminException,
)
from src.domains.users.models import User
from src.domains.users.repositories import UserRepository
from src.domains.users.schemas import BaseUserSchema, UserSchema

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository: UserRepository = user_repository

    async def get_current_user(self, payload: dict) -> User:
        """Получение юзера по id"""
        user_id = int(payload.get("sub"))
        user = await self.user_repository.find_one(user_id)
        if not user:
            raise UserDoesNotExist
        return user

    async def get_current_admin_user(self, payload: dict) -> User:
        """Получение админ-пользователя"""
        try:
            user = await self.get_current_user(payload)
            if not user.is_admin:
                raise UserNotAdminException
            return user
        except UserNotAdminException:
            raise
        except Exception as err:
            logger.error(f"Ошибка авторизации: {err}")
            raise HTTPException(status_code=400, detail=f"Ошибка авторизации: {err}")

    async def get_current_active_user(self, payload: dict) -> User:
        """Получение активного юзера"""
        try:
            user = await self.get_current_user(payload)
            if not user.is_active:
                raise UserNotActiveException
            return user
        except UserNotActiveException:
            raise
        except Exception as err:
            logger.error(f"Ошибка авторизации: {err}")
            raise HTTPException(status_code=400, detail=f"Ошибка авторизации: {err}")

    async def authenticate_user(self, user_data: BaseUserSchema) -> JSONResponse:
        """Аутентифицировать юзера"""
        try:
            user = await self.user_repository.find_by_username(user_data.username)
            if (
                not user
                or not jwt_auth.verify_password(user_data.password, user.hashed_password.encode())
                or not user.is_active
            ):
                raise InvalidCredentialsException

            access_token = jwt_auth.create_token(user.id)
            refresh_token = jwt_auth.create_token(user.id, token_type=conf.jwt_auth.REFRESH_TOKEN_TYPE)

            response = JSONResponse({"message": "Login successful"})
            jwt_auth.set_token_in_cookie(
                response=response,
                token=access_token,
                token_type=conf.jwt_auth.ACCESS_TOKEN_TYPE,
                expire_minutes=conf.jwt_auth.ACCESS_TOKEN_EXPIRE_MINUTES,
            )
            jwt_auth.set_token_in_cookie(
                response=response,
                token=refresh_token,
                token_type=conf.jwt_auth.REFRESH_TOKEN_TYPE,
                expire_timedelta=timedelta(days=conf.jwt_auth.REFRESH_TOKEN_EXPIRE_DAYS),
            )
            return response
        except InvalidCredentialsException:
            raise
        except Exception:
            raise

    async def refresh(self, current_user: UserSchema) -> JSONResponse:
        """Обновляет access токен и устанавливает его в куки"""
        try:
            new_access_token = jwt_auth.create_token(current_user.id)

            response = JSONResponse({"message": "Access токен успешно обновлен"})
            jwt_auth.set_token_in_cookie(
                response=response,
                token=new_access_token,
                token_type=conf.jwt_auth.ACCESS_TOKEN_TYPE,
                expire_minutes=conf.jwt_auth.ACCESS_TOKEN_EXPIRE_MINUTES,
            )
            return response
        except Exception:
            raise

    async def logout_user(self) -> JSONResponse:
        """Удаление coookie с токенами доступа"""
        response = JSONResponse({"message": "Успешный выход пользователя"})
        response.delete_cookie(conf.jwt_auth.ACCESS_TOKEN_TYPE + conf.jwt_auth.COOKIE_KEY)
        response.delete_cookie(conf.jwt_auth.REFRESH_TOKEN_TYPE + conf.jwt_auth.COOKIE_KEY)
        return response

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response

from src.core.exceptions import AUTH_EXEPTIONS
from src.domains.auth.dependencies import auth_service, get_current_user, get_current_user_by_refresh
from src.domains.auth.services import AuthService
from src.domains.users.schemas import BaseUserSchema, UserSchema

logger = logging.getLogger(__name__)

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Страница не найдена"}},
)


@auth_router.post("/login/", summary="Аутентификация пользователя")
async def auth_user_for_jwt(
    auth_service: Annotated[AuthService, Depends(auth_service)], user_data: BaseUserSchema
) -> Response:
    try:
        return await auth_service.authenticate_user(user_data)
    except AUTH_EXEPTIONS:
        raise
    except Exception as e:
        logger.exception(f"Ошибка аутентификации пользователя {user_data.username}: {e}")
        raise HTTPException(status_code=400, detail="Ошибка аутентификации пользователя")


@auth_router.get("/logout/", summary="Деаутентификация пользователя", dependencies=[Depends(get_current_user)])
async def logout(auth_service: Annotated[AuthService, Depends(auth_service)]):
    try:
        return await auth_service.logout_user()
    except AUTH_EXEPTIONS:
        raise
    except Exception as e:
        logging.exception(f"Ошибка при выходе пользователя: {e}")
        raise HTTPException(status_code=400, detail="Ошибка при выходе пользователя")


@auth_router.post("/refresh/", summary="Обновление токенов с помощью refresh")
async def auth_refresh_jwt(
    auth_service: Annotated[AuthService, Depends(auth_service)],
    current_user: UserSchema = Depends(get_current_user_by_refresh),
):
    try:
        return await auth_service.refresh(current_user)
    except AUTH_EXEPTIONS:
        raise
    except Exception as e:
        logger.exception(f"Ошибка аутентификации пользователя: {e}")
        raise HTTPException(status_code=400, detail="Ошибка аутентификации пользователя")

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from src.core.exceptions import AUTH_EXEPTIONS, InvalidCredentialsException
from src.domains.auth.dependencies import (
    get_current_admin_user,
    get_current_user,
)
from src.domains.users.dependencies import user_service
from src.domains.users.schemas import BaseUserSchema, UpdateUserSchema, UserSchema
from src.domains.users.services import UserService

logger = logging.getLogger(__name__)

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"Описание": "Страницы не найдена"}},
)


@user_router.get(
    "/",
    summary="Получить всех зарегистрированных пользователей",
    response_model=list[UserSchema],
    dependencies=[Depends(get_current_admin_user)],
)
async def get_all_users(user_service: Annotated[UserService, Depends(user_service)]):
    try:
        users = await user_service.user_repository.find_all()
        return users
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logger.exception(f"Ошибка получения данных: {err}")
        raise HTTPException(status_code=400, detail=f"Ошибка получения данных: {err}")


@user_router.get("/me/", summary="Получить информацию о текущем пользователе", response_model=UserSchema)
async def auth_user_check_self_info(current_user: UserSchema = Depends(get_current_user)):
    try:
        return current_user
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logger.exception(f"Ошибка получения данных: {err}")
        raise HTTPException(status_code=400, detail=f"Ошибка получения данных: {err}")


@user_router.patch("/me/update/", summary="Обновить текущего пользователя", response_model=UserSchema)
async def update_user(
    user_data: UpdateUserSchema,
    user_service: Annotated[UserService, Depends(user_service)],
    current_user: UserSchema = Depends(get_current_user),
):
    try:
        user = await user_service.update_user(id=current_user.id, user_data=user_data)
        return user
    except AUTH_EXEPTIONS:
        raise
    except Exception as e:
        logger.exception(f"Ошибка обновления данных: {e}")
        raise HTTPException(status_code=400, detail="Ошибка обновления данных")


@user_router.post("/register/", summary="Зарегистрировать нового порльзователя", response_model=UserSchema)
async def register_new_user(user_data: BaseUserSchema, user_service: Annotated[UserService, Depends(user_service)]):
    try:
        user = await user_service.register_user(user_data)
        return user
    except InvalidCredentialsException:
        raise
    except Exception as e:
        logger.exception(f"Ошибка регистрации пользователя {user_data.username}: {e}")
        raise HTTPException(status_code=400, detail="Ошибка регистрации пользователя")

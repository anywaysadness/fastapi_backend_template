import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from src.core.exceptions import AUTH_EXEPTIONS, InvalidCredentialsException
from src.domains.auth.dependencies import auth_service, get_current_admin_user
from src.domains.users.dependencies import user_service
from src.domains.users.schemas import BaseUserSchema, UserSchema
from src.domains.users.services import UserService

logger = logging.getLogger(__name__)

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"Описание": "Страницы не найдена"}},
)


@user_router.get("/me/")
async def auth_user_check_self_info(user: UserSchema = Depends(auth_service().get_current_auth_user)):
    try:
        return user
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logger.exception(f"Ошибка получения данных: {err}")
        raise HTTPException(status_code=400, detail=f"Ошибка получения данных: {err}")


@user_router.get("/", response_model=list[UserSchema], dependencies=[Depends(get_current_admin_user)])
async def get_all_users(user_service: Annotated[UserService, Depends(user_service)]):
    try:
        users = await user_service.user_repository.find_all()
        return users
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logger.exception(f"Ошибка получения данных: {err}")
        raise HTTPException(status_code=400, detail=f"Ошибка получения данных: {err}")


@user_router.post("/register/", response_model=UserSchema)
async def register_new_user(user_data: BaseUserSchema, user_service: Annotated[UserService, Depends(user_service)]):
    try:
        user = await user_service.register_user(user_data)
        return user
    except InvalidCredentialsException:
        raise
    except Exception as e:
        logger.exception(f"Ошибка регистрации пользователя {user_data.username}: {e}")
        raise HTTPException(status_code=400, detail="Ошибка регистрации пользователя")

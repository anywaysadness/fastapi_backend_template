import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException

from src.core.exceptions import InvalidCredentialsException
from src.domains.auth.dependencies import auth_service
from src.domains.auth.services import AuthService
from src.domains.users.schemas import BaseUserSchema

logger = logging.getLogger(__name__)

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Страница не найдена"}},
)


@auth_router.post("/login/")
async def auth_user_for_jwt(
    auth_service: Annotated[AuthService, Depends(auth_service)],
    username: str = Form(...),
    password: str = Form(...),
):
    try:
        user_data = BaseUserSchema(username=username, password=password)
        user = await auth_service.check_user_exists(user_data)
        return await auth_service.create_access_token(user)
    except InvalidCredentialsException:
        raise
    except Exception as e:
        logger.exception(f"Ошибка аутентификации пользователя {username}: {e}")
        raise HTTPException(status_code=400, detail="Ошибка аутентификации пользователя")

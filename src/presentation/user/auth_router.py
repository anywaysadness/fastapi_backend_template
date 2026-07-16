import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response

from src.application.users.auth_user import UserAuthUseCase
from src.application.users.register_user import UserRegistrationUseCase
from src.common.base_exception import BaseDomainException
from src.common.configuration import conf
from src.di.auth_dependencies import registration_user_use_case, user_auth_use_case
from src.presentation.user.schemas import BaseUserSchema, ResponseUserSchema
from src.presentation.user.security import set_token_cookie

logger = logging.getLogger(__name__)

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Страница не найдена"}},
)


@auth_router.post("/login", summary="Аутентификация пользователя")
async def login(
    user_data: BaseUserSchema,
    response: Response,
    use_case: Annotated[UserAuthUseCase, Depends(user_auth_use_case)],
) -> dict[str, str]:
    try:
        result = await use_case.user_authentication(user_data)
        set_token_cookie(
            response,
            key=conf.jwt_auth.ACCESS_TOKEN_TYPE + conf.jwt_auth.COOKIE_KEY,
            value=result.access_token,
            max_age=result.access_token_max_age,
        )
        set_token_cookie(
            response,
            key=conf.jwt_auth.REFRESH_TOKEN_TYPE + conf.jwt_auth.COOKIE_KEY,
            value=result.refresh_token,
            max_age=result.refresh_token_max_age,
        )

        return {"message": "OK"}

    except BaseDomainException as be:
        logger.exception(f"Ошибка аутентификации пользователя {user_data.username}: {be}")
        raise HTTPException(status_code=be.status_code, detail=be.message)
    except Exception as e:
        logger.exception(f"Ошибка аутентификации пользователя {user_data.username}: {e}")
        raise HTTPException(status_code=400, detail="Ошибка аутентификации пользователя")


@auth_router.post("/register", summary="Регистрация пользователя", status_code=201, response_model=ResponseUserSchema)
async def register(
    user_data: BaseUserSchema,
    use_case: Annotated[UserRegistrationUseCase, Depends(registration_user_use_case)],
):
    try:
        user = await use_case.user_registration(user_data)
        return user.to_dict()
    except BaseDomainException as be:
        logger.exception(f"Ошибка регистрации пользователя {user_data.username}: {be}")
        raise HTTPException(status_code=be.status_code, detail=be.message)
    except Exception as e:
        logger.exception(f"Ошибка регистрации пользователя {user_data.username}: {e}")
        raise HTTPException(status_code=400, detail="Ошибка регистрации пользователя")

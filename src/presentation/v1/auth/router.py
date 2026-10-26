from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from src.application.auth import ChangePasswordUseCase, DeactivateAccountUseCase, LoginUserUseCase, LogoutUserUseCase
from src.application.auth.dto import LoginCommand
from src.di.auth import (
    auth_cookie_scheme,
    get_change_password_use_case,
    get_current_user,
    get_deactivate_account_use_case,
    get_login_use_case,
    get_logout_use_case,
)
from src.domains.users.entities import UserEntity
from src.presentation.v1.auth.cookies import clear_auth_cookie, set_auth_cookie
from src.presentation.v1.auth.schemas import (
    ChangePasswordRequest,
    DeactivateAccountRequest,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    UserResponse,
)
from src.presentation.v1.responses import (
    INVALID_CREDENTIALS,
    INVALID_SESSION_OR_PASSWORD,
    RATE_LIMITED,
    REDIS_UNAVAILABLE,
    UNAUTHORIZED,
)

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(
    "/login",
    response_model=LoginResponse,
    summary="Аутентификация пользователя",
    response_description="Успешная аутентификация, access-токен установлен в cookie",
    responses={
        401: INVALID_CREDENTIALS,
        429: RATE_LIMITED,
        503: REDIS_UNAVAILABLE,
    },
)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    use_case: Annotated[LoginUserUseCase, Depends(get_login_use_case)],
) -> LoginResponse:
    """Проверяет учётные данные, создаёт сессию в Redis и устанавливает HttpOnly cookie.

    Повторные попытки ограничены по IP и username.
    """
    result = await use_case.execute(
        LoginCommand(
            username=payload.username,
            password=payload.password,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    )
    set_auth_cookie(response, result.access_token, result.expires_in)
    response.headers["Cache-Control"] = "no-store"
    return LoginResponse()


@auth_router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Выход из аккаунта",
    response_description="Сессия отозвана, cookie удалена",
    responses={503: REDIS_UNAVAILABLE},
)
async def logout(
    response: Response,
    token: Annotated[str | None, Depends(auth_cookie_scheme)],
    use_case: Annotated[LogoutUserUseCase, Depends(get_logout_use_case)],
) -> LogoutResponse:
    """Отзывает текущую сессию по `jti` и удаляет cookie.

    Отсутствующий или невалидный токен не считается ошибкой.
    """
    try:
        await use_case.execute(token)
    finally:
        clear_auth_cookie(response)
    response.headers["Cache-Control"] = "no-store"
    return LogoutResponse()


@auth_router.get(
    "/me",
    response_model=UserResponse,
    summary="Текущий пользователь",
    response_description="Данные пользователя из активной сессии",
    responses={
        401: UNAUTHORIZED,
        503: REDIS_UNAVAILABLE,
    },
)
async def me(
    current_user: Annotated[UserEntity, Depends(get_current_user)],
) -> UserResponse:
    """Возвращает пользователя из access-JWT с проверкой активной серверной сессии."""
    return UserResponse.from_entity(current_user)


@auth_router.post(
    "/change-password",
    response_model=LoginResponse,
    summary="Смена пароля",
    response_description="Пароль изменён, все сессии отозваны",
    responses={
        401: INVALID_SESSION_OR_PASSWORD,
        503: REDIS_UNAVAILABLE,
    },
)
async def change_password(
    payload: ChangePasswordRequest,
    response: Response,
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    use_case: Annotated[ChangePasswordUseCase, Depends(get_change_password_use_case)],
) -> LoginResponse:
    """Меняет пароль после проверки текущего и отзывает все сессии пользователя.

    Cookie с access-токеном очищается, поэтому требуется повторный вход.
    """
    if current_user.id is None:
        raise RuntimeError("Authenticated user must have an id")
    await use_case.execute(current_user.id, payload.current_password, payload.new_password)
    clear_auth_cookie(response)
    response.headers["Cache-Control"] = "no-store"
    return LoginResponse()


@auth_router.post(
    "/deactivate",
    response_model=LoginResponse,
    summary="Деактивация аккаунта",
    response_description="Аккаунт деактивирован, все сессии отозваны",
    responses={
        401: INVALID_SESSION_OR_PASSWORD,
        503: REDIS_UNAVAILABLE,
    },
)
async def deactivate_account(
    payload: DeactivateAccountRequest,
    response: Response,
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    use_case: Annotated[DeactivateAccountUseCase, Depends(get_deactivate_account_use_case)],
) -> LoginResponse:
    """Деактивирует аккаунт после подтверждения паролем и отзывает все сессии.

    Cookie с access-токеном очищается, поэтому требуется повторный вход.
    """
    if current_user.id is None:
        raise RuntimeError("Authenticated user must have an id")
    await use_case.execute(current_user.id, payload.password)
    clear_auth_cookie(response)
    response.headers["Cache-Control"] = "no-store"
    return LoginResponse()

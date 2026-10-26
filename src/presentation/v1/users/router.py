from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from src.application.users.dto import RegisterUserCommand
from src.application.users.register_user import RegisterUserUseCase
from src.di.users import get_register_user_use_case
from src.presentation.v1.responses import CONFLICT, RATE_LIMITED, REDIS_UNAVAILABLE
from src.presentation.v1.users.schemas import RegisterUserRequest, UserResponse

users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя",
    response_description="Созданный пользователь",
    responses={
        409: CONFLICT,
        429: RATE_LIMITED,
        503: REDIS_UNAVAILABLE,
    },
)
async def register(
    payload: RegisterUserRequest,
    request: Request,
    use_case: Annotated[RegisterUserUseCase, Depends(get_register_user_use_case)],
) -> UserResponse:
    """Создаёт пользователя с нормализованным username и Argon2id-хешем пароля.

    Cookie не устанавливается; для получения токена используйте `/api/v1/auth/login`.
    """
    user = await use_case.execute(
        RegisterUserCommand(
            username=payload.username,
            password=payload.password,
            ip_address=request.client.host if request.client else None,
        )
    )
    return UserResponse.from_entity(user)

"""Переиспользуемые описания ответов для OpenAPI."""

from typing import Any

from pydantic import Field

from src.common.base_schemas import BaseSchema


class ErrorResponse(BaseSchema):
    """Ответ с безопасным описанием ошибки."""

    detail: str = Field(description="Текст ошибки для клиента", examples=["Неверные учётные данные"])


INVALID_CREDENTIALS: dict[str, Any] = {
    "model": ErrorResponse,
    "description": "Неверные учётные данные или неактивный аккаунт",
    "content": {"application/json": {"example": {"detail": "Неверные учётные данные"}}},
}

UNAUTHORIZED: dict[str, Any] = {
    "model": ErrorResponse,
    "description": "Токен отсутствует, повреждён, просрочен или отозван",
    "content": {"application/json": {"example": {"detail": "Невалидный токен"}}},
}

INVALID_SESSION_OR_PASSWORD: dict[str, Any] = {
    "model": ErrorResponse,
    "description": "Невалидная сессия или неверный текущий пароль",
    "content": {"application/json": {"example": {"detail": "Неверные учётные данные"}}},
}

CONFLICT: dict[str, Any] = {
    "model": ErrorResponse,
    "description": "Пользователь с таким username уже существует",
    "content": {"application/json": {"example": {"detail": "Пользователь 'alice' уже существует"}}},
}

RATE_LIMITED: dict[str, Any] = {
    "model": ErrorResponse,
    "description": "Превышен лимит попыток для IP и username",
    "content": {"application/json": {"example": {"detail": "Слишком много попыток. Повторите позже"}}},
}

REDIS_UNAVAILABLE: dict[str, Any] = {
    "model": ErrorResponse,
    "description": "Redis временно недоступен, операция отклонена fail-closed",
    "content": {"application/json": {"example": {"detail": "Сервис временно недоступен"}}},
}

from datetime import datetime
from typing import Self

from pydantic import EmailStr, Field, field_validator

from src.common.base_schemas import BaseSchema
from src.common.password_policy import validate_password_strength
from src.domains.users.entities import UserEntity


class RegisterUserRequest(BaseSchema):
    """Данные для регистрации нового пользователя."""

    username: str = Field(
        min_length=3,
        max_length=128,
        description="Username: 3–128 символов, латиница, цифры, точка, дефис или подчёркивание",
        examples=["alice"],
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Пароль: строчная и заглавная латинские буквы, цифра и специальный символ",
        examples=["StrongPass1!"],
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """Проверяет сложность пароля."""
        return validate_password_strength(value)


class UserResponse(BaseSchema):
    """Публичное представление пользователя."""

    id: int = Field(description="Идентификатор пользователя", examples=[1])
    username: str = Field(description="Нормализованный username", examples=["alice"])
    email: EmailStr | None = Field(
        default=None,
        description="Email пользователя",
        examples=["alice@example.com"],
    )
    is_active: bool = Field(description="Признак активного аккаунта", examples=[True])
    is_admin: bool = Field(description="Признак администратора", examples=[False])
    created_at: datetime = Field(
        description="Дата создания",
        examples=["2026-10-26T12:00:00Z"],
    )
    updated_at: datetime | None = Field(
        default=None,
        description="Дата последнего изменения",
        examples=["2026-10-26T12:00:00Z"],
    )

    @classmethod
    def from_entity(cls, user: UserEntity) -> Self:
        """Преобразует доменную сущность в ответ API."""
        if user.id is None:
            raise ValueError("Persisted user must have an id")
        return cls(
            id=user.id,
            username=user.username.value,
            email=user.email.value if user.email else None,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

from pydantic import Field, field_validator

from src.common.base_schemas import BaseSchema
from src.common.password_policy import validate_password_strength
from src.presentation.v1.users.schemas import UserResponse

__all__ = ["LoginRequest", "LoginResponse", "LogoutResponse", "UserResponse"]


class LoginRequest(BaseSchema):
    """Учётные данные для входа."""

    username: str = Field(
        min_length=1,
        max_length=128,
        description="Username (регистр не важен)",
        examples=["alice"],
    )
    password: str = Field(
        min_length=1,
        max_length=128,
        description="Пароль пользователя",
        examples=["StrongPass1!"],
    )


class LoginResponse(BaseSchema):
    """Ответ на успешный вход."""

    message: str = Field(default="OK", description="Результат операции", examples=["OK"])


class LogoutResponse(BaseSchema):
    """Ответ на выход из аккаунта."""

    message: str = Field(default="OK", description="Результат операции", examples=["OK"])


class ChangePasswordRequest(BaseSchema):
    """Данные для смены пароля."""

    current_password: str = Field(
        min_length=1,
        max_length=128,
        description="Текущий пароль",
        examples=["StrongPass1!"],
    )
    new_password: str = Field(
        min_length=8,
        max_length=128,
        description="Новый пароль: строчная и заглавная латинские буквы, цифра и специальный символ",
        examples=["NewStrongPass2!"],
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        """Проверяет сложность нового пароля."""
        return validate_password_strength(value)


class DeactivateAccountRequest(BaseSchema):
    """Подтверждение деактивации аккаунта."""

    password: str = Field(
        min_length=1,
        max_length=128,
        description="Текущий пароль для подтверждения",
        examples=["StrongPass1!"],
    )

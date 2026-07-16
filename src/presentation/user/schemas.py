from datetime import datetime

from pydantic import EmailStr

from src.common.base_schemas import BaseSchema


class TokenInfo(BaseSchema):
    access_token: str
    refresh_token: str | None = None


class ResponseUserSchema(BaseSchema):
    username: str
    created_at: datetime
    email: EmailStr | None = None
    is_active: bool = True
    is_admin: bool = False


class BaseUserSchema(BaseSchema):
    username: str
    password: str


class UpdateUserSchema(BaseUserSchema):
    email: EmailStr | None = None
    is_active: bool = True
    is_admin: bool = False

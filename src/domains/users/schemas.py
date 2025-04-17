from datetime import datetime

from pydantic import EmailStr

from src.core.base_schemas import BaseSchema


class UserSchema(BaseSchema):
    id: int
    username: str
    hashed_password: bytes
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

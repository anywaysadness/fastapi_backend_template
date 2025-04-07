from typing import Annotated

from pydantic import EmailStr

from src.core.base_schema import BaseSchema


class UserSchema(BaseSchema):
    id: int
    username: str
    hashed_password: bytes
    email: EmailStr | None = None
    is_active: bool = True


class CreateUserSchema(BaseSchema):
    username: str
    password: str


class UpdateUserSchema(BaseSchema):
    username: str
    password: bytes
    email: EmailStr | None = None
    is_active: bool = True

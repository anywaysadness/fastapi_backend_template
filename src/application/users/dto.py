# src/application/auth/dto.py
from dataclasses import dataclass

from src.domains.users.entities.user import UserEntity


@dataclass(frozen=True)
class AuthResult:
    user: UserEntity
    access_token: str
    refresh_token: str
    access_token_max_age: int
    refresh_token_max_age: int

from dataclasses import dataclass

from src.domains.users.entities import UserEntity


@dataclass(frozen=True)
class LoginCommand:
    """Данные для входа пользователя."""

    username: str
    password: str
    ip_address: str | None = None
    user_agent: str | None = None


@dataclass(frozen=True)
class LoginResult:
    """Результат успешного входа."""

    user: UserEntity
    access_token: str
    expires_in: int

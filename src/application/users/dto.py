from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterUserCommand:
    """Данные для регистрации пользователя."""

    username: str
    password: str
    ip_address: str | None = None

from dataclasses import dataclass

from src.common.base_value_object import BaseValueObject
from src.domains.auth.exceptions import InvalidPasswordError


@dataclass(frozen=True)
class PasswordVO(BaseValueObject[str]):
    """Пароль пользователя."""

    value: str

    def __post_init__(self) -> None:
        """Проверяет непустой пароль допустимой длины."""
        if not self.value or len(self.value) > 128:
            raise InvalidPasswordError()

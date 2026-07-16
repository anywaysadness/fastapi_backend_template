from dataclasses import dataclass

from src.common.base_value_object import BaseValueObject


@dataclass(frozen=True)
class PasswordVO(BaseValueObject[str]):
    """Пароль пользователя"""

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("Password cannot be empty")

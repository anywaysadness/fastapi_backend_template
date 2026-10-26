import re
from dataclasses import dataclass

from src.common.base_value_object import BaseValueObject
from src.domains.users.exceptions import InvalidUsernameError


@dataclass(frozen=True)
class UsernameVO(BaseValueObject[str]):
    """Нормализованный юзернейм пользователя."""

    value: str

    _USERNAME_PATTERN = re.compile(r"^[a-z0-9_.-]+$")

    def __post_init__(self) -> None:
        """Нормализует и проверяет username."""
        normalized = self.value.strip().lower()

        if (
            not 3 <= len(normalized) <= 128
            or not self._USERNAME_PATTERN.fullmatch(normalized)
            or normalized[0] in "._-"
            or normalized[-1] in "._-"
        ):
            raise InvalidUsernameError(self.value)

        object.__setattr__(self, "value", normalized)

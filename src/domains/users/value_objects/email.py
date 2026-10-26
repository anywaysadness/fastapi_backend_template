import re
from dataclasses import dataclass

from src.common.base_value_object import BaseValueObject
from src.domains.users.exceptions import InvalidEmailError


@dataclass(frozen=True)
class EmailVO(BaseValueObject[str]):
    """Email пользователя."""

    value: str

    _EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    def __post_init__(self) -> None:
        """Нормализует и проверяет email."""
        normalized = self.value.strip().lower()

        if len(normalized) > 512 or not self._EMAIL_PATTERN.fullmatch(normalized):
            raise InvalidEmailError(normalized)

        object.__setattr__(self, "value", normalized)

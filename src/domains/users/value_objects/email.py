import re
from dataclasses import dataclass

from src.common.base_value_object import BaseValueObject
from src.domains.users.exceptions import InvalidEmailError


@dataclass(frozen=True)
class EmailVO(BaseValueObject[str]):
    """email пользователя"""

    value: str

    _EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()

        if not self._EMAIL_PATTERN.match(normalized):
            raise InvalidEmailError(normalized)

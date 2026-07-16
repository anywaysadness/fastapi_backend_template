from dataclasses import dataclass

from src.common.base_value_object import BaseValueObject


@dataclass(frozen=True)
class UsernameVO(BaseValueObject):
    """Юзернейм пользователя"""

    value: str

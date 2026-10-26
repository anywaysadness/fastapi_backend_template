from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

VT = TypeVar("VT", bound=Any)


@dataclass(frozen=True)
class BaseValueObject(ABC, Generic[VT]):
    """Неизменяемое значение, валидируемое при создании."""

    value: VT


@dataclass(frozen=True)
class BaseIdObject(BaseValueObject):
    """Value object, которое валидирует своё значение после инициализации."""

    def __post_init__(self) -> None:
        """Запускает валидацию значения."""
        self._validate()

    @abstractmethod
    def _validate(self) -> None:
        """Проверяет корректность значения."""
        raise NotImplementedError

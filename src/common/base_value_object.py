from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

VT = TypeVar("VT", bound=Any)


@dataclass(frozen=True)
class BaseValueObject(ABC, Generic[VT]):
    value: VT


@dataclass(frozen=True)
class BaseIdObject(BaseValueObject):
    def __post_init__(self):
        self._validate()

    @abstractmethod
    def _validate(self) -> None:
        raise NotImplementedError

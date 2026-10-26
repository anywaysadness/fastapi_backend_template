from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(kw_only=True)
class BaseEvent(ABC):
    """Базовое доменное событие с уникальным идентификатором."""

    event_id: UUID = field(default_factory=uuid4)


@dataclass(kw_only=True)
class DomainEvent(BaseEvent):
    """Событие, которое можно сериализовать для публикации."""

    @abstractmethod
    def to_dict(self) -> dict:
        """Возвращает представление события в виде словаря."""
        pass

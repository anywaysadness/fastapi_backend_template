from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(kw_only=True)
class BaseEvent(ABC):
    event_id: UUID = field(default_factory=uuid4)


@dataclass(kw_only=True)
class DomainEvent(BaseEvent):
    @abstractmethod
    def to_dict(self) -> dict:
        pass

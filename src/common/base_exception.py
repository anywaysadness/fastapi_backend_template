from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class BaseDomainException(ABC, Exception):
    """Базовый класс для всех доменных исключений."""

    @property
    @abstractmethod
    def message(self) -> str:
        """Возвращает безопасное сообщение для клиента."""
        raise NotImplementedError

    @property
    def status_code(self) -> int:
        """Возвращает HTTP-статус для маппинга исключения."""
        return 422

    def __str__(self) -> str:
        """Возвращает сообщение исключения для логов."""
        return self.message

from dataclasses import dataclass

from src.common.base_exception import BaseDomainException


@dataclass
class RateLimitExceededError(BaseDomainException):
    """Превышен лимит попыток для операции."""

    @property
    def message(self) -> str:
        """Возвращает сообщение для клиента."""
        return "Слишком много попыток. Повторите позже"

    @property
    def status_code(self) -> int:
        """Возвращает HTTP-статус ошибки."""
        return 429


@dataclass
class RateLimiterUnavailableError(BaseDomainException):
    """Сервис rate limiting недоступен."""

    @property
    def message(self) -> str:
        """Возвращает сообщение для клиента."""
        return "Сервис ограничения запросов временно недоступен"

    @property
    def status_code(self) -> int:
        """Возвращает HTTP-статус ошибки."""
        return 503

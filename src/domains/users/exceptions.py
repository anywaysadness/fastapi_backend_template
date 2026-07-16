from dataclasses import dataclass

from src.common.base_exception import BaseDomainException


@dataclass(frozen=True)
class InvalidEmailError(BaseDomainException):
    email: str

    @property
    def message(self) -> str:
        return f"Неверный формат email '{self.email}'"


@dataclass(frozen=True)
class UserNotFoundError(BaseDomainException):
    @property
    def message(self) -> str:
        return "Пользователь не найден"

    @property
    def status_code(self) -> int:
        return 404

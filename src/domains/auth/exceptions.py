from dataclasses import dataclass

from src.common.base_exception import BaseDomainException


@dataclass(frozen=True)
class UserAlreadyExistsException(BaseDomainException):
    username: str

    @property
    def message(self) -> str:
        return f"Пользователь '{self.username}' уже существует"

    @property
    def status_code(self) -> int:
        return 409


@dataclass(frozen=True)
class UserNotFoundException(BaseDomainException):
    username: str

    @property
    def message(self) -> str:
        return f"Пользователя '{self.username}' не существует"

    @property
    def status_code(self) -> int:
        return 404


@dataclass(frozen=True)
class InvalidCredentialsError(BaseDomainException):
    @property
    def message(self) -> str:
        return "Неверные учётные данные"

    @property
    def status_code(self) -> int:
        return 401

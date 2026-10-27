from dataclasses import dataclass

from src.common.base_exception import BaseDomainException


@dataclass
class InvalidEmailError(BaseDomainException):
    """Email имеет неверный формат."""

    email: str

    @property
    def message(self) -> str:
        """Возвращает сообщение для клиента."""
        return f"Неверный формат email '{self.email}'"


@dataclass
class InvalidUsernameError(BaseDomainException):
    """Username не соответствует допустимому формату."""

    username: str

    @property
    def message(self) -> str:
        """Возвращает сообщение для клиента."""
        return (
            "Юзернейм должен содержать от 3 до 128 символов и состоять только из латинских букв, цифр, '.', '_' или '-'"
        )


@dataclass
class UserNotFoundError(BaseDomainException):
    """Пользователь не найден."""

    @property
    def message(self) -> str:
        """Возвращает сообщение для клиента."""
        return "Пользователь не найден"

    @property
    def status_code(self) -> int:
        """Возвращает HTTP-статус ошибки."""
        return 404

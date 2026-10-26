from dataclasses import dataclass

from src.common.base_exception import BaseDomainException


@dataclass
class UserAlreadyExistsException(BaseDomainException):
    """Пользователь с таким username уже существует."""

    username: str

    @property
    def message(self) -> str:
        """Возвращает сообщение для клиента."""
        return f"Пользователь '{self.username}' уже существует"

    @property
    def status_code(self) -> int:
        """Возвращает HTTP-статус ошибки."""
        return 409


@dataclass
class UserNotFoundException(BaseDomainException):
    """Запрошенный пользователь не найден."""

    username: str

    @property
    def message(self) -> str:
        """Возвращает сообщение для клиента."""
        return f"Пользователя '{self.username}' не существует"

    @property
    def status_code(self) -> int:
        """Возвращает HTTP-статус ошибки."""
        return 404


@dataclass
class InvalidCredentialsError(BaseDomainException):
    """Неверные учётные данные или неактивный аккаунт."""

    @property
    def message(self) -> str:
        """Возвращает сообщение для клиента."""
        return "Неверные учётные данные"

    @property
    def status_code(self) -> int:
        """Возвращает HTTP-статус ошибки."""
        return 401


@dataclass
class InvalidPasswordError(BaseDomainException):
    """Пароль не соответствует ограничениям длины."""

    @property
    def message(self) -> str:
        """Возвращает сообщение для клиента."""
        return "Пароль должен содержать от 1 до 128 символов"

    @property
    def status_code(self) -> int:
        """Возвращает HTTP-статус ошибки."""
        return 422


@dataclass
class WeakPasswordError(BaseDomainException):
    """Пароль не соответствует политике сложности."""

    @property
    def message(self) -> str:
        """Возвращает сообщение для клиента."""
        return "Пароль должен содержать строчную и заглавную латинские буквы, цифру и специальный символ"

    @property
    def status_code(self) -> int:
        """Возвращает HTTP-статус ошибки."""
        return 422


@dataclass
class InvalidTokenError(BaseDomainException):
    """Токен отсутствует, повреждён, просрочен или отозван."""

    @property
    def message(self) -> str:
        """Возвращает сообщение для клиента."""
        return "Невалидный токен"

    @property
    def status_code(self) -> int:
        """Возвращает HTTP-статус ошибки."""
        return 401


@dataclass
class NotAuthorizedError(BaseDomainException):
    """Запрос требует аутентификации."""

    @property
    def message(self) -> str:
        """Возвращает сообщение для клиента."""
        return "Пользователь не авторизован"

    @property
    def status_code(self) -> int:
        """Возвращает HTTP-статус ошибки."""
        return 401


@dataclass
class ForbiddenError(BaseDomainException):
    """У пользователя недостаточно прав."""

    @property
    def message(self) -> str:
        """Возвращает сообщение для клиента."""
        return "Недостаточно прав"

    @property
    def status_code(self) -> int:
        """Возвращает HTTP-статус ошибки."""
        return 403


@dataclass
class SessionStorageUnavailableError(BaseDomainException):
    """Хранилище сессий временно недоступно."""

    @property
    def message(self) -> str:
        """Возвращает сообщение для клиента."""
        return "Сервис сессий временно недоступен"

    @property
    def status_code(self) -> int:
        """Возвращает HTTP-статус ошибки."""
        return 503

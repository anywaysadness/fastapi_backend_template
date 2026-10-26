from typing import Protocol


class PasswordHasher(Protocol):
    """Порт хеширования и проверки паролей."""

    def hash(self, raw_password: str) -> str:
        """Возвращает хеш пароля."""
        ...

    def verify(self, raw_password: str, hashed_password: str) -> bool:
        """Проверяет пароль по сохранённому хешу."""
        ...

    def verify_dummy(self, raw_password: str) -> None:
        """Выполняет фиктивную проверку для выравнивания времени ответа."""
        ...

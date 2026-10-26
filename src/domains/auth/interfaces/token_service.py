from typing import Any, Protocol
from uuid import UUID


class TokenService(Protocol):
    """Порт выпуска и проверки access-токенов."""

    @property
    def access_token_ttl_seconds(self) -> int:
        """Возвращает время жизни access-токена в секундах."""
        ...

    def create_access_token(self, user_id: int, session_id: UUID) -> str:
        """Создаёт access-токен для пользователя и сессии."""
        ...

    def decode(self, token: str) -> dict[str, Any]:
        """Проверяет подпись и срок действия токена."""
        ...

    def validate_type(self, payload: dict[str, Any], expected_type: str) -> None:
        """Проверяет назначение токена."""
        ...

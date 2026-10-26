from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import jwt
from jwt import PyJWTError

from src.domains.auth.exceptions import InvalidTokenError
from src.domains.auth.interfaces import TokenService


class JwtService(TokenService):
    """PyJWT-адаптер для access-токенов."""

    _TOKEN_TYPE_FIELD = "type"

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        *,
        expire_minutes: int = 720,
        issuer: str = "fastapi-backend-template",
        audience: str = "fastapi-backend-template-api",
    ) -> None:
        """Сохраняет параметры подписи и проверки токенов."""
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._expire_minutes = expire_minutes
        self._issuer = issuer
        self._audience = audience

    @property
    def access_token_ttl_seconds(self) -> int:
        """Возвращает TTL access-токена в секундах."""
        return self._expire_minutes * 60

    def create_access_token(self, user_id: int, session_id: UUID) -> str:
        """Создаёт подписанный access-токен с `jti` сессии."""
        now = datetime.now(UTC)
        payload = {
            "sub": str(user_id),
            "jti": str(session_id),
            self._TOKEN_TYPE_FIELD: "access",
            "iss": self._issuer,
            "aud": self._audience,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=self._expire_minutes)).timestamp()),
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def decode(self, token: str) -> dict[str, Any]:
        """Проверяет подпись, срок действия, issuer и audience."""
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
                audience=self._audience,
                issuer=self._issuer,
                options={"require": ["exp", "iat", "sub", "jti", "type", "iss", "aud"]},
            )
        except PyJWTError as exc:
            raise InvalidTokenError() from exc

        if not isinstance(payload, dict):
            raise InvalidTokenError()
        return payload

    def validate_type(self, payload: dict[str, Any], expected_type: str) -> None:
        """Проверяет назначение токена."""
        if payload.get(self._TOKEN_TYPE_FIELD) != expected_type:
            raise InvalidTokenError()

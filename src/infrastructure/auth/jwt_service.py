from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from jwt import InvalidTokenError


class JwtService:
    def __init__(self, secret_key: str, algorithm: str) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._token_type_field = "type"

    def create_access_token(self, user_id: int, expire_minutes: int = 30) -> str:
        return self._create_token(user_id, "access", timedelta(minutes=expire_minutes))

    def create_refresh_token(self, user_id: int, expire_days: int = 30) -> str:
        return self._create_token(user_id, "refresh", timedelta(days=expire_days))

    def decode(self, token: str) -> dict:
        try:
            return jwt.decode(token, self._secret_key, algorithms=[self._algorithm], options={"verify_exp": True})
        except JWTError as e:
            raise InvalidTokenError from e

    def validate_type(self, payload: dict, expected_type: str) -> None:
        if payload.get(self._token_type_field) != expected_type:
            raise InvalidTokenError

    def _create_token(self, user_id: int, token_type: str, lifetime: timedelta) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": str(user_id),
            self._token_type_field: token_type,
            "exp": int((now + lifetime).timestamp()),
            "iat": int(now.timestamp()),
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

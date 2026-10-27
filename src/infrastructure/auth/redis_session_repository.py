import json
from typing import Any
from uuid import UUID

from redis.asyncio import Redis
from redis.exceptions import RedisError

from src.domains.auth.exceptions import SessionStorageUnavailableError
from src.domains.auth.interfaces import SessionRepository

_SESSION_KEY = "auth:session:{session_id}"
_USER_SESSIONS_KEY = "auth:user_sessions:{user_id}"


class RedisSessionRepository(SessionRepository):
    """Redis-хранилище сессий с TTL и индексом по пользователю.

    Репозиторий работает только с сырыми JSON-данными и не восстанавливает
    доменную сущность: это делает ``SessionService``.
    """

    def __init__(self, redis_client: Redis) -> None:
        """Сохраняет асинхронный Redis-клиент."""
        self._redis = redis_client

    async def save(self, session_data: dict[str, Any], ttl_seconds: int) -> None:
        """Сохраняет сериализованную сессию и добавляет её в индекс пользователя."""
        session_id = str(session_data["id"])
        user_sessions_key = _USER_SESSIONS_KEY.format(user_id=session_data["user_id"])

        try:
            await self._redis.set(
                _SESSION_KEY.format(session_id=session_id),
                json.dumps(session_data),
                ex=ttl_seconds,
            )
            await self._redis.sadd(user_sessions_key, session_id)
            await self._redis.expire(user_sessions_key, ttl_seconds)
        except RedisError as exc:
            raise SessionStorageUnavailableError() from exc

    async def get_by_id(self, session_id: UUID) -> dict[str, Any] | None:
        """Возвращает сырые данные сессии или удаляет повреждённую запись."""
        key = _SESSION_KEY.format(session_id=session_id)
        try:
            raw_session = await self._redis.get(key)
        except RedisError as exc:
            raise SessionStorageUnavailableError() from exc

        if raw_session is None:
            return None

        try:
            if isinstance(raw_session, bytes):
                raw_session = raw_session.decode()
            data = json.loads(raw_session)
        except (json.JSONDecodeError, TypeError, ValueError):
            await self._redis.delete(key)
            return None

        if not isinstance(data, dict):
            await self._redis.delete(key)
            return None

        return data

    async def revoke_by_id(self, session_id: UUID) -> None:
        """Удаляет сессию и её запись из индекса пользователя."""
        key = _SESSION_KEY.format(session_id=session_id)
        try:
            raw_session = await self._redis.get(key)
            await self._redis.delete(key)
            if raw_session is not None:
                if isinstance(raw_session, bytes):
                    raw_session = raw_session.decode()
                data = json.loads(raw_session)
                if isinstance(data, dict):
                    await self._redis.srem(
                        _USER_SESSIONS_KEY.format(user_id=data["user_id"]),
                        str(session_id),
                    )
        except RedisError as exc:
            raise SessionStorageUnavailableError() from exc
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            return

    async def revoke_by_user_id(self, user_id: int) -> int:
        """Удаляет все сессии пользователя."""
        user_sessions_key = _USER_SESSIONS_KEY.format(user_id=user_id)
        try:
            session_ids = await self._redis.smembers(user_sessions_key)
            if not session_ids:
                return 0

            keys = []
            for session_id in session_ids:
                if isinstance(session_id, bytes):
                    session_id = session_id.decode()
                keys.append(_SESSION_KEY.format(session_id=session_id))

            deleted = await self._redis.delete(*keys)
            await self._redis.delete(user_sessions_key)
            return int(deleted)
        except RedisError as exc:
            raise SessionStorageUnavailableError() from exc

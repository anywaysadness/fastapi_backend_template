import json
from datetime import UTC, datetime
from uuid import UUID

from redis.asyncio import Redis
from redis.exceptions import RedisError

from src.domains.auth.entities import Session
from src.domains.auth.exceptions import SessionStorageUnavailableError
from src.domains.auth.interfaces import SessionRepository

_SESSION_KEY = "auth:session:{session_id}"
_USER_SESSIONS_KEY = "auth:user_sessions:{user_id}"


class RedisSessionRepository(SessionRepository):
    """Redis-хранилище сессий с TTL и индексом по пользователю."""

    def __init__(self, redis_client: Redis) -> None:
        """Сохраняет асинхронный Redis-клиент."""
        self._redis = redis_client

    async def save(self, session: Session) -> None:
        """Сохраняет сессию и добавляет её в индекс пользователя."""
        ttl = max(1, int((session.expires_at - datetime.now(UTC)).total_seconds()))
        user_sessions_key = _USER_SESSIONS_KEY.format(user_id=session.user_id)

        try:
            await self._redis.set(
                _SESSION_KEY.format(session_id=session.id),
                json.dumps(session.to_dict()),
                ex=ttl,
            )
            await self._redis.sadd(user_sessions_key, str(session.id))
            await self._redis.expire(user_sessions_key, ttl)
        except RedisError as exc:
            raise SessionStorageUnavailableError() from exc

    async def get_by_id(self, session_id: UUID) -> Session | None:
        """Возвращает валидную сессию или удаляет повреждённую."""
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
            session = Session.from_dict(json.loads(raw_session))
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            await self._redis.delete(key)
            return None

        if not session.is_valid():
            await self.revoke_by_id(session.id)
            return None

        return session

    async def revoke_by_id(self, session_id: UUID) -> None:
        """Удаляет сессию и её запись из индекса пользователя."""
        key = _SESSION_KEY.format(session_id=session_id)
        try:
            raw_session = await self._redis.get(key)
            await self._redis.delete(key)
            if raw_session is not None:
                if isinstance(raw_session, bytes):
                    raw_session = raw_session.decode()
                session = Session.from_dict(json.loads(raw_session))
                await self._redis.srem(
                    _USER_SESSIONS_KEY.format(user_id=session.user_id),
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

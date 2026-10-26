import hashlib
from typing import cast

from redis.asyncio import Redis
from redis.exceptions import RedisError

from src.application.common.exceptions import RateLimiterUnavailableError
from src.application.common.rate_limiter import RateLimiter

_RATE_LIMIT_SCRIPT = """
local current = redis.call('INCR', KEYS[1])
if current == 1 or redis.call('TTL', KEYS[1]) < 0 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return current
"""


class RedisRateLimiter(RateLimiter):
    """Атомарный fixed-window rate limiter на Redis."""

    def __init__(self, redis_client: Redis) -> None:
        """Сохраняет асинхронный Redis-клиент."""
        self._redis = redis_client

    async def allow(
        self,
        *,
        scope: str,
        identity: str,
        limit: int,
        window_seconds: int,
    ) -> bool:
        """Увеличивает счётчик и проверяет лимит в рамках окна."""
        key = self._build_key(scope, identity)
        try:
            current = cast(
                int,
                await self._redis.eval(
                    _RATE_LIMIT_SCRIPT,
                    1,
                    key,
                    window_seconds,
                ),
            )
        except RedisError as exc:
            raise RateLimiterUnavailableError() from exc

        return current <= limit

    @staticmethod
    def _build_key(scope: str, identity: str) -> str:
        """Строит ключ без хранения исходного IP и username."""
        digest = hashlib.sha256(identity.encode()).hexdigest()
        return f"auth:rate_limit:{scope}:{digest}"

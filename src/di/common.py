from fastapi import Depends, Request
from redis.asyncio import Redis

from src.application.common.rate_limiter import RateLimiter
from src.domains.uow import UnitOfWork
from src.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from src.infrastructure.rate_limit import RedisRateLimiter


def get_uow() -> UnitOfWork:
    """Создаёт Unit of Work для текущего запроса."""
    return SqlAlchemyUnitOfWork()


def get_redis_client(request: Request) -> Redis:
    """Возвращает Redis-клиент, созданный в lifespan приложения."""
    return request.app.state.redis


def get_rate_limiter(redis_client: Redis = Depends(get_redis_client)) -> RateLimiter:
    """Создаёт Redis-ограничитель попыток."""
    return RedisRateLimiter(redis_client)

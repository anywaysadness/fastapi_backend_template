import asyncio
import logging
import time
from collections.abc import Awaitable, Callable, Sequence

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from src.infrastructure.database.connection import engine

logger = logging.getLogger(__name__)

_STARTUP_LOCK_KEY = 7_234_921


async def _connect_with_retry(timeout: float) -> AsyncConnection:
    """Подключается к БД с ограниченным числом повторов."""
    started_at = time.monotonic()
    while True:
        try:
            return await engine.connect()
        except Exception as exc:
            if time.monotonic() - started_at >= timeout:
                raise
            logger.warning("Database is not ready yet: %s", exc)
            await asyncio.sleep(1.0)


async def _acquire_startup_lock(connection: AsyncConnection, timeout: float) -> None:
    """Ждёт освобождения advisory lock для startup-задач."""
    started_at = time.monotonic()
    while True:
        acquired = await connection.scalar(
            text("SELECT pg_try_advisory_lock(:key)"),
            {"key": _STARTUP_LOCK_KEY},
        )
        if acquired:
            return
        if time.monotonic() - started_at >= timeout:
            raise TimeoutError("Timed out waiting for the startup advisory lock")
        await asyncio.sleep(0.5)


async def run_startup_tasks(
    tasks: Sequence[tuple[str, Callable[[], Awaitable[None]]]],
    *,
    lock_timeout: float = 120.0,
    task_timeout: float = 300.0,
) -> None:
    """Выполняет startup-задачи ровно в одном процессе за раз."""
    connection = await _connect_with_retry(lock_timeout)
    try:
        await _acquire_startup_lock(connection, lock_timeout)
        try:
            for name, task in tasks:
                logger.info("Running startup task: %s", name)
                await asyncio.wait_for(task(), timeout=task_timeout)
                logger.info("Startup task completed: %s", name)
        finally:
            await connection.execute(
                text("SELECT pg_advisory_unlock(:key)"),
                {"key": _STARTUP_LOCK_KEY},
            )
            await connection.commit()
    finally:
        await connection.close()

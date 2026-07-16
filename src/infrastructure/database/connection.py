import asyncio
import logging
import sys
from collections.abc import Callable
from subprocess import PIPE, run

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from src.common.configuration import conf

# Создание асинхронного движка
engine: AsyncEngine = create_async_engine(
    url=conf.postgres.build_connection_str(),
    echo=conf.app.DEBUG,  # Вывод SQL-запросов в консоль (только в режиме отладки)
    pool_pre_ping=True,  # Автоматическая проверка соединений в пуле
)

# Фабрика сессий для работы с базой данных
async_session_maker: Callable[..., AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Не истекать объекты после коммита
)


async def get_async_session():
    async with async_session_maker() as session:
        yield session


async def migrate(retry_delay: float = 5.0) -> None:
    """Бесконечно пытается применить миграции Alembic до успеха."""
    attempt = 0
    while True:
        attempt += 1
        try:
            run(
                [sys.executable, "-m", "alembic", "upgrade", "head"],
                check=True,
                capture_output=True,
            )
            logging.debug("Миграции БД успешно применены")
            return
        except Exception as e:
            logging.warning(
                "Сбой миграции БД (попытка %d): %s. Повтор через %.1f сек.",
                attempt,
                e,
                retry_delay,
            )
            await asyncio.sleep(retry_delay)

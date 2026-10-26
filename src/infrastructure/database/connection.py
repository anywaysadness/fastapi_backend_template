import asyncio
import logging
import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from src.common.configuration import conf

logger = logging.getLogger(__name__)

engine: AsyncEngine = create_async_engine(
    url=conf.postgres.build_connection_str(),
    echo=conf.app.DEBUG,
    pool_pre_ping=True,
)

async_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def migrate(timeout: float = 120.0) -> None:
    """Применяет миграции Alembic без блокировки event loop."""
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "alembic",
        "upgrade",
        "head",
        cwd=Path(__file__).resolve().parents[3],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
    except TimeoutError:
        process.kill()
        await process.communicate()
        raise RuntimeError(f"Alembic migration timed out after {timeout} seconds") from None

    if process.returncode != 0:
        error = stderr.decode(errors="replace").strip() or stdout.decode(errors="replace").strip()
        logger.error("Alembic migration failed: %s", error)
        raise RuntimeError("Alembic migration failed")

    logger.info("Database migrations applied")


async def check_database() -> None:
    """Проверяет доступность PostgreSQL."""
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))


async def close_database() -> None:
    """Закрывает пул соединений SQLAlchemy."""
    await engine.dispose()

import sys
from subprocess import run

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.configuration import conf

# Создание асинхронного движка
engine = create_async_engine(
    url=conf.postgres_conf.build_connection_str(),
    echo=conf.app_conf.app_debug,  # Вывод SQL-запросов в консоль (только в режиме отладки)
    pool_pre_ping=True,  # Автоматическая проверка соединений в пуле
)

# Фабрика сессий для работы с базой данных
async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Не истекать объекты после коммита
)


async def migrate() -> None:
    """Применяет миграции Alembic"""
    try:
        run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            check=True,
        )
        print("Migrations applied successfully.")
    except Exception as e:
        print(f"Migration failed: {e}")

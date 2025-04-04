from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from redis.asyncio import Redis as redis_async
from sqlalchemy.engine import URL

load_dotenv()


class PostgresConfig(BaseSettings):
    """Базовые настройки для POSTGRES"""

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    database_system: str = "postgresql"

    def build_connection_str(self, driver: str | None = "asyncpg") -> str:
        return URL.create(
            drivername=f"{self.database_system}+{driver}",
            username=self.postgres_user,
            database=self.postgres_db,
            password=self.postgres_password,
            port=self.postgres_port,
            host=self.postgres_host,
        ).render_as_string(hide_password=False)


class RedisConfig(BaseSettings):
    """Базовые настройки для REDIS"""

    redis_db: int = 0
    redis_host: str = "localhost"
    redis_port: int = 6379
    database_system: str = "redis"

    def build_connection_str_for_redis(self) -> str:
        """Создает строку подключения к REDIS"""
        return f"{self.database_system}://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    def get_async_redis_connection(self) -> redis_async:
        """Возвращает асинхронное соединение с REDIS"""
        redis_url = self.build_connection_str_for_redis()
        return redis_async.from_url(redis_url)


class AppConfig(BaseSettings):
    """Базовые настройки Приложения"""

    app_env: str = "development"
    app_debug: bool = True


class Configuration:
    postgres_conf = PostgresConfig()
    redis_conf = RedisConfig()
    app_conf = AppConfig()


conf = Configuration()

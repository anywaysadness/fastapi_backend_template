import logging

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

    convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


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

    def get_app_settings(self):
        if self.app_env == "production":
            return {
                "prefix": "api",
                "enable_dev": False,
                "log_level": logging.WARNING,
            }
        elif self.app_env == "development":
            return {
                "prefix": "dev",
                "enable_dev": True,
                "log_level": logging.INFO,
            }
        else:
            return {
                "prefix": "dev",
                "enable_dev": True,
                "log_level": logging.INFO,
            }


class JWTAuth(BaseSettings):
    SECRET_KEY: str
    COOKIE_KEY: str = "_auth_token"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 6
    ALGORITHM: str = "HS256"
    TOKEN_TYPE_FIELD: str = "type"
    ACCESS_TOKEN_TYPE: str = "access"
    REFRESH_TOKEN_TYPE: str = "refresh"


class Configuration:
    postgres_conf = PostgresConfig()
    redis_conf = RedisConfig()
    app_conf = AppConfig()
    jwt_auth = JWTAuth()


conf = Configuration()

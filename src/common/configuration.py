import logging

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from redis.asyncio import Redis as redis_async
from sqlalchemy.engine import URL

load_dotenv()

_BASE_CONFIG = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    case_sensitive=True,
    extra="ignore",
)


class PostgresConfig(BaseSettings):
    """Базовые настройки для POSTGRES"""

    model_config = SettingsConfigDict(env_prefix="POSTGRES_", **_BASE_CONFIG)

    USER: str
    PASSWORD: str
    DB: str
    HOST: str = "localhost"
    PORT: int = 5432
    DATABASE_SYSTEM: str = "postgresql"

    def build_connection_str(self, driver: str | None = "asyncpg") -> str:
        return URL.create(
            drivername=f"{self.DATABASE_SYSTEM}+{driver}",
            username=self.USER,
            database=self.DB,
            password=self.PASSWORD,
            port=self.PORT,
            host=self.HOST,
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

    model_config = SettingsConfigDict(env_prefix="REDIS_", **_BASE_CONFIG)

    HOST: str = "localhost"
    PORT: int = 6379
    DB: int = 0
    DATABASE_SYSTEM: str = "redis"

    def build_connection_str_for_redis(self) -> str:
        """Создает строку подключения к REDIS"""
        return f"{self.DATABASE_SYSTEM}://{self.HOST}:{self.PORT}/{self.DB}"

    def get_async_redis_connection(self) -> redis_async:
        """Возвращает асинхронное соединение с REDIS"""
        redis_url = self.build_connection_str_for_redis()
        return redis_async.from_url(redis_url)


class AppConfig(BaseSettings):
    """Базовые настройки Приложения"""

    model_config = SettingsConfigDict(env_prefix="APP_", **_BASE_CONFIG)

    ENV: str = "development"
    DEBUG: bool = True

    def get_app_settings(self):
        if self.ENV == "production":
            return {
                "prefix": "api",
                "enable_dev": False,
                "log_level": logging.WARNING,
            }
        elif self.ENV == "development":
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


class JWTAuthConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="JWT_", **_BASE_CONFIG)

    SECRET_KEY: str
    COOKIE_KEY: str = "_auth_token"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 6
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_TYPE: str = "access"
    REFRESH_TOKEN_TYPE: str = "refresh"


class TokenConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TOKEN_", **_BASE_CONFIG)

    SECRET_KEY: str
    TOKEN_HMAC_DIGEST_MODE: str = "sha256"
    TOKEN_DEFAULT_ENCODING: str = "utf-8"


class Configuration:
    jwt_auth = JWTAuthConfig()
    token: TokenConfig = TokenConfig()
    postgres = PostgresConfig()
    redis = RedisConfig()
    app = AppConfig()


conf = Configuration()

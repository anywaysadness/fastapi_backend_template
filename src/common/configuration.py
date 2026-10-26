from typing import ClassVar, Literal
from urllib.parse import quote

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

_BASE_CONFIG = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    case_sensitive=True,
    extra="ignore",
)

_INSECURE_MARKERS = ("change-me", "changeme", "_test_", "example")


class PostgresConfig(BaseSettings):
    """Настройки подключения к PostgreSQL."""

    model_config = SettingsConfigDict(env_prefix="POSTGRES_", **_BASE_CONFIG)

    USER: str
    PASSWORD: SecretStr
    DB: str
    HOST: str = "localhost"
    PORT: int = 5432
    DATABASE_SYSTEM: str = "postgresql"

    convention: ClassVar[dict[str, str]] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    def build_connection_str(self, driver: str | None = "asyncpg") -> str:
        """Собирает URL подключения к PostgreSQL."""
        return URL.create(
            drivername=f"{self.DATABASE_SYSTEM}+{driver}" if driver else self.DATABASE_SYSTEM,
            username=self.USER,
            database=self.DB,
            password=self.PASSWORD.get_secret_value(),
            port=self.PORT,
            host=self.HOST,
        ).render_as_string(hide_password=False)


class RedisConfig(BaseSettings):
    """Настройки подключения к Redis."""

    model_config = SettingsConfigDict(env_prefix="REDIS_", **_BASE_CONFIG)

    HOST: str = "localhost"
    PORT: int = 6379
    DB: int = 0
    PASSWORD: SecretStr | None = None
    DATABASE_SYSTEM: str = "redis"

    def build_connection_str_for_redis(self) -> str:
        """Собирает URL подключения к Redis."""
        credentials = ""
        if self.PASSWORD is not None and self.PASSWORD.get_secret_value():
            credentials = f":{quote(self.PASSWORD.get_secret_value(), safe='')}@"
        return f"{self.DATABASE_SYSTEM}://{credentials}{self.HOST}:{self.PORT}/{self.DB}"


class AppConfig(BaseSettings):
    """Настройки приложения и HTTP-слоя."""

    model_config = SettingsConfigDict(env_prefix="APP_", **_BASE_CONFIG)

    ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str] = Field(default_factory=list)
    COOKIE_SECURE: bool = True
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"
    COOKIE_DOMAIN: str | None = None
    AUTH_COOKIE_NAME: str = "authorization"

    @property
    def is_development(self) -> bool:
        """Возвращает True для development-окружения."""
        return self.ENV == "development"

    @model_validator(mode="after")
    def validate_http_settings(self) -> "AppConfig":
        """Проверяет безопасность CORS и cookie-настроек."""
        if "*" in self.CORS_ORIGINS:
            raise ValueError("CORS_ORIGINS must contain explicit origins instead of '*'")
        if self.COOKIE_SAMESITE == "none" and not self.COOKIE_SECURE:
            raise ValueError("COOKIE_SECURE must be enabled when COOKIE_SAMESITE is 'none'")
        return self


class JWTAuthConfig(BaseSettings):
    """Настройки access-токенов."""

    model_config = SettingsConfigDict(env_prefix="JWT_", **_BASE_CONFIG)

    SECRET_KEY: SecretStr = Field(min_length=32)
    ALGORITHM: Literal["HS256", "HS384", "HS512"] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=720, gt=0)
    ISSUER: str = "fastapi-backend-template"
    AUDIENCE: str = "fastapi-backend-template-api"


class PasswordConfig(BaseSettings):
    """Настройки хеширования паролей."""

    model_config = SettingsConfigDict(env_prefix="PASSWORD_", **_BASE_CONFIG)

    PEPPER: SecretStr = SecretStr("")
    ARGON2_TIME_COST: int = Field(default=3, ge=1)
    ARGON2_MEMORY_COST: int = Field(default=65536, ge=8192)
    ARGON2_PARALLELISM: int = Field(default=4, ge=1)


class RateLimitConfig(BaseSettings):
    """Настройки ограничения попыток аутентификации."""

    model_config = SettingsConfigDict(env_prefix="RATE_LIMIT_", **_BASE_CONFIG)

    LOGIN_ATTEMPTS: int = Field(default=5, gt=0)
    LOGIN_WINDOW_SECONDS: int = Field(default=60, gt=0)
    REGISTER_ATTEMPTS: int = Field(default=10, gt=0)
    REGISTER_WINDOW_SECONDS: int = Field(default=3600, gt=0)


class Configuration:
    """Корневая конфигурация приложения."""

    def __init__(self) -> None:
        """Загружает настройки из окружения и проверяет production-секреты."""
        self.app = AppConfig()
        self.jwt_auth = JWTAuthConfig()  # type: ignore[call-arg]
        self.password = PasswordConfig()
        self.rate_limit = RateLimitConfig()
        self.postgres = PostgresConfig()  # type: ignore[call-arg]
        self.redis = RedisConfig()
        self._validate_production_secrets()

    def _validate_production_secrets(self) -> None:
        """Запрещает слабые и примерные секреты в production."""
        if self.app.ENV != "production":
            return

        secrets = {
            "JWT_SECRET_KEY": self.jwt_auth.SECRET_KEY.get_secret_value(),
            "PASSWORD_PEPPER": self.password.PEPPER.get_secret_value(),
        }
        for name, value in secrets.items():
            if len(value) < 32:
                raise ValueError(f"{name} must be at least 32 characters in production")
            if any(marker in value.lower() for marker in _INSECURE_MARKERS):
                raise ValueError(f"{name} must not use an example or test value in production")


conf = Configuration()

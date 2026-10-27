import os

os.environ["APP_ENV"] = "development"
os.environ["APP_DEBUG"] = "False"
os.environ["APP_LOG_LEVEL"] = "WARNING"
os.environ["APP_COOKIE_SECURE"] = "False"
os.environ["APP_CORS_ORIGINS"] = "[]"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-0123456789abcdef0123456789"
os.environ["PASSWORD_PEPPER"] = "test-pepper-0123456789abcdef0123456789"
os.environ["POSTGRES_USER"] = "postgres"
os.environ["POSTGRES_PASSWORD"] = "postgres"
os.environ["POSTGRES_DB"] = "app_db"
os.environ["REDIS_HOST"] = "localhost"

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from src.di.auth import get_auth_service, get_password_hasher, get_session_repository
from src.di.common import get_rate_limiter, get_uow
from src.domains.auth.auth_service import AuthService
from src.infrastructure.auth import Argon2PasswordHasher
from src.main import create_app
from tests.fakes import (
    InMemoryRateLimiter,
    InMemorySessionRepository,
    InMemoryUnitOfWork,
    InMemoryUserRepository,
)


@pytest.fixture
def user_repository() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def session_repository() -> InMemorySessionRepository:
    return InMemorySessionRepository()


@pytest.fixture
def rate_limiter() -> InMemoryRateLimiter:
    return InMemoryRateLimiter()


@pytest.fixture
def app(user_repository, session_repository, rate_limiter):
    application = create_app()
    password_hasher = Argon2PasswordHasher(
        pepper="test-pepper",
        time_cost=1,
        memory_cost=8192,
        parallelism=1,
    )

    async def override_uow() -> AsyncGenerator[InMemoryUnitOfWork]:
        yield InMemoryUnitOfWork(user_repository)

    def override_session_repository() -> InMemorySessionRepository:
        return session_repository

    def override_password_hasher() -> Argon2PasswordHasher:
        return password_hasher

    def override_auth_service() -> AuthService:
        return AuthService(password_hasher=password_hasher)

    def override_rate_limiter() -> InMemoryRateLimiter:
        return rate_limiter

    application.dependency_overrides[get_uow] = override_uow
    application.dependency_overrides[get_session_repository] = override_session_repository
    application.dependency_overrides[get_password_hasher] = override_password_hasher
    application.dependency_overrides[get_auth_service] = override_auth_service
    application.dependency_overrides[get_rate_limiter] = override_rate_limiter

    yield application
    application.dependency_overrides.clear()


@pytest.fixture
async def client(app) -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client

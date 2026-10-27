from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from src.domains.auth.entities import Session
from src.domains.auth.services import SessionService
from src.domains.users.entities import UserEntity
from src.domains.users.services import UserService
from src.domains.users.value_objects import UsernameVO
from tests.fakes import (
    InMemorySessionRepository,
    InMemoryUnitOfWork,
    InMemoryUserRepository,
)


@dataclass
class UserRow:
    """Строка БД пользователя для проверки преобразования."""

    id: int
    username: str
    hashed_password: str
    email: str | None
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_admin: bool


def test_user_service_maps_row_to_entity_and_back() -> None:
    now = datetime.now(UTC)
    row = UserRow(
        id=7,
        username="Alice",
        hashed_password="hashed-password",
        email="Foo@Bar.com",
        created_at=now,
        updated_at=now,
        is_active=True,
        is_admin=False,
    )
    service = UserService(InMemoryUnitOfWork(InMemoryUserRepository()))

    user = service.to_entity(row)

    assert user.id == 7
    assert user.username.value == "alice"
    assert user.hashed_password == "hashed-password"
    assert user.email is not None
    assert user.email.value == "foo@bar.com"
    assert user.created_at == now
    assert user.updated_at == now
    assert user.is_active is True
    assert user.is_admin is False
    assert service.to_persistence(user) == {
        "id": 7,
        "username": "alice",
        "hashed_password": "hashed-password",
        "created_at": now,
        "updated_at": now,
        "email": "foo@bar.com",
        "is_active": True,
        "is_admin": False,
    }


def test_user_service_maps_missing_email_to_none() -> None:
    now = datetime.now(UTC)
    row = UserRow(
        id=8,
        username="bob",
        hashed_password="hashed-password",
        email=None,
        created_at=now,
        updated_at=now,
        is_active=True,
        is_admin=False,
    )

    service = UserService(InMemoryUnitOfWork(InMemoryUserRepository()))
    user = service.to_entity(row)

    assert user.email is None
    assert service.to_persistence(user)["email"] is None


def test_session_service_maps_storage_payload_to_entity_and_back() -> None:
    session_id = uuid4()
    created_at = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    expires_at = created_at + timedelta(minutes=5)
    payload = {
        "id": str(session_id),
        "user_id": 42,
        "created_at": created_at.isoformat(),
        "expires_at": expires_at.isoformat(),
        "ip_address": "127.0.0.1",
        "user_agent": "test-agent",
        "revoked_at": None,
    }
    service = SessionService(InMemorySessionRepository())

    session = service.to_entity(payload)

    assert session.id == session_id
    assert session.user_id == 42
    assert session.created_at == created_at
    assert session.expires_at == expires_at
    assert session.ip_address == "127.0.0.1"
    assert session.user_agent == "test-agent"
    assert session.revoked_at is None
    assert service.to_persistence(session) == payload


async def test_user_service_saves_through_repository() -> None:
    repository = InMemoryUserRepository()
    service = UserService(InMemoryUnitOfWork(repository))
    user = UserEntity.create(
        username=UsernameVO("Alice"),
        hashed_password="hashed-password",
    )

    saved = await service.save(user)

    assert saved.id == 1
    assert saved.username.value == "alice"
    assert repository.users[1].username == "alice"


async def test_session_service_revokes_expired_session() -> None:
    repository = InMemorySessionRepository()
    service = SessionService(repository)
    session = Session.create(
        user_id=1,
        expires_at=datetime.now(UTC) - timedelta(seconds=1),
    )
    await service.save(session)

    assert await service.get_by_id(session.id) is None
    assert session.id not in repository.sessions

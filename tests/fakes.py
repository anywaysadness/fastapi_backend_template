from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Self
from uuid import UUID

from src.domains.users.exceptions import UserNotFoundError
from src.domains.users.value_objects import UsernameVO


@dataclass
class FakeUserRecord:
    """Инфраструктурная запись пользователя для тестов."""

    id: int
    username: str
    hashed_password: str
    email: str | None
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    is_admin: bool = False


class InMemoryUserRepository:
    def __init__(self) -> None:
        self.users: dict[int, FakeUserRecord] = {}
        self._next_id = 1

    async def get_by_id(self, user_id: int) -> FakeUserRecord | None:
        return self.users.get(user_id)

    async def find_by_username(self, username: UsernameVO) -> FakeUserRecord | None:
        return next((user for user in self.users.values() if user.username == username.value), None)

    async def find_all(self, limit: int = 100, offset: int = 0) -> list[FakeUserRecord]:
        return list(self.users.values())[offset : offset + limit]

    async def create(self, data: dict[str, Any]) -> FakeUserRecord:
        user_id = self._next_id
        self._next_id += 1
        now = datetime.now(UTC)
        record = FakeUserRecord(
            id=user_id,
            username=str(data["username"]),
            hashed_password=str(data["hashed_password"]),
            email=data.get("email"),
            created_at=data.get("created_at") or now,
            updated_at=data.get("updated_at") or now,
            is_active=bool(data.get("is_active", True)),
            is_admin=bool(data.get("is_admin", False)),
        )
        self.users[user_id] = record
        return record

    async def update(self, user_id: int, data: dict[str, Any]) -> FakeUserRecord:
        record = self.users.get(user_id)
        if record is None:
            raise UserNotFoundError()

        for field, value in data.items():
            setattr(record, field, value)
        return record


class InMemoryUnitOfWork:
    def __init__(self, users: InMemoryUserRepository) -> None:
        self.users = users

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        return None

    async def commit(self) -> None:
        return None

    async def rollback(self) -> None:
        return None


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self.allowed = True
        self.error: Exception | None = None
        self.calls: list[tuple[str, str, int, int]] = []

    async def allow(
        self,
        *,
        scope: str,
        identity: str,
        limit: int,
        window_seconds: int,
    ) -> bool:
        self.calls.append((scope, identity, limit, window_seconds))
        if self.error is not None:
            raise self.error
        return self.allowed


class InMemorySessionRepository:
    def __init__(self) -> None:
        self.sessions: dict[UUID, dict[str, Any]] = {}

    async def save(self, session_data: dict[str, Any], ttl_seconds: int) -> None:
        self.sessions[UUID(str(session_data["id"]))] = session_data

    async def get_by_id(self, session_id: UUID) -> dict[str, Any] | None:
        return self.sessions.get(session_id)

    async def revoke_by_id(self, session_id: UUID) -> None:
        self.sessions.pop(session_id, None)

    async def revoke_by_user_id(self, user_id: int) -> int:
        session_ids = [
            session_id for session_id, session_data in self.sessions.items() if int(session_data["user_id"]) == user_id
        ]
        for session_id in session_ids:
            self.sessions.pop(session_id, None)
        return len(session_ids)

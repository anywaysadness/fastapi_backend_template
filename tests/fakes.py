from uuid import UUID

from src.domains.auth.entities import Session
from src.domains.users.entities import UserEntity
from src.domains.users.value_objects import UsernameVO


class InMemoryUserRepository:
    def __init__(self) -> None:
        self.users: dict[int, UserEntity] = {}
        self._next_id = 1

    async def save(self, user: UserEntity) -> UserEntity:
        if user.id is None:
            user.id = self._next_id
            self._next_id += 1
        self.users[user.id] = user
        return user

    async def get_by_id(self, user_id: int) -> UserEntity | None:
        return self.users.get(user_id)

    async def find_by_username(self, username: UsernameVO) -> UserEntity | None:
        return next((user for user in self.users.values() if user.username.value == username.value), None)

    async def find_all(self, limit: int = 100, offset: int = 0) -> list[UserEntity]:
        return list(self.users.values())[offset : offset + limit]


class InMemoryUnitOfWork:
    def __init__(self, users: InMemoryUserRepository) -> None:
        self.users = users

    async def __aenter__(self) -> "InMemoryUnitOfWork":
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
        self.sessions: dict[UUID, Session] = {}

    async def save(self, session: Session) -> None:
        self.sessions[session.id] = session

    async def get_by_id(self, session_id: UUID) -> Session | None:
        session = self.sessions.get(session_id)
        if session is None or not session.is_valid():
            return None
        return session

    async def revoke_by_id(self, session_id: UUID) -> None:
        self.sessions.pop(session_id, None)

    async def revoke_by_user_id(self, user_id: int) -> int:
        session_ids = [session_id for session_id, session in self.sessions.items() if session.user_id == user_id]
        for session_id in session_ids:
            self.sessions.pop(session_id, None)
        return len(session_ids)

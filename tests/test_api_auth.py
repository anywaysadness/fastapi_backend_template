from httpx import AsyncClient

from src.application.common.exceptions import RateLimiterUnavailableError
from tests.fakes import InMemoryRateLimiter, InMemoryUserRepository


async def register(
    client: AsyncClient,
    username: str = "Alice",
    password: str = "StrongPass1!",
):
    return await client.post(
        "/api/v1/users/register",
        json={"username": username, "password": password},
    )


async def test_register_normalizes_username_and_hides_secrets(client: AsyncClient) -> None:
    response = await register(client)

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "alice"
    assert body["is_admin"] is False
    assert body["is_active"] is True
    assert "hashed_password" not in body


async def test_register_rejects_weak_password_and_extra_fields(client: AsyncClient) -> None:
    weak = await register(client, password="weak")
    assert weak.status_code == 422
    assert "weak" not in weak.text

    extra_field = await client.post(
        "/api/v1/users/register",
        json={"username": "bob", "password": "StrongPass1!", "is_admin": True},
    )
    assert extra_field.status_code == 422


async def test_register_rate_limit_returns_429(
    client: AsyncClient,
    rate_limiter: InMemoryRateLimiter,
) -> None:
    rate_limiter.allowed = False

    response = await register(client)

    assert response.status_code == 429
    assert rate_limiter.calls[-1][0] == "register"


async def test_duplicate_username_returns_409(client: AsyncClient) -> None:
    assert (await register(client)).status_code == 201
    duplicate = await register(client, username="ALICE")

    assert duplicate.status_code == 409


async def test_login_me_logout_flow(client: AsyncClient, session_repository) -> None:
    assert (await register(client)).status_code == 201

    wrong_password = await client.post(
        "/api/v1/auth/login",
        json={"username": "alice", "password": "WrongPass1!"},
    )
    assert wrong_password.status_code == 401

    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "ALICE", "password": "StrongPass1!"},
    )
    assert login.status_code == 200
    assert client.cookies.get("authorization")
    assert len(session_repository.sessions) == 1

    me = await client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["username"] == "alice"

    logout = await client.post("/api/v1/auth/logout")
    assert logout.status_code == 200
    assert not session_repository.sessions
    assert (await client.get("/api/v1/auth/me")).status_code == 401


async def test_login_rate_limit_returns_429(
    client: AsyncClient,
    rate_limiter: InMemoryRateLimiter,
) -> None:
    assert (await register(client)).status_code == 201
    rate_limiter.allowed = False

    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "alice", "password": "StrongPass1!"},
    )

    assert response.status_code == 429
    assert rate_limiter.calls[-1][0] == "login"


async def test_rate_limiter_failure_is_fail_closed(
    client: AsyncClient,
    rate_limiter: InMemoryRateLimiter,
) -> None:
    rate_limiter.error = RateLimiterUnavailableError()

    response = await register(client)

    assert response.status_code == 503


async def test_me_requires_valid_session(
    client: AsyncClient,
    user_repository: InMemoryUserRepository,
    session_repository,
) -> None:
    assert (await register(client)).status_code == 201
    assert (await client.get("/api/v1/auth/me")).status_code == 401

    assert (
        await client.post(
            "/api/v1/auth/login",
            json={"username": "alice", "password": "StrongPass1!"},
        )
    ).status_code == 200
    assert (await client.get("/api/v1/auth/me")).status_code == 200

    session_repository.sessions.clear()
    assert (await client.get("/api/v1/auth/me")).status_code == 401


async def test_inactive_user_cannot_login(
    client: AsyncClient,
    user_repository: InMemoryUserRepository,
) -> None:
    assert (await register(client)).status_code == 201
    next(iter(user_repository.users.values())).is_active = False

    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "alice", "password": "StrongPass1!"},
    )
    assert response.status_code == 401


async def test_change_password_revokes_all_sessions(client: AsyncClient, session_repository) -> None:
    assert (await register(client)).status_code == 201
    assert (
        await client.post(
            "/api/v1/auth/login",
            json={"username": "alice", "password": "StrongPass1!"},
        )
    ).status_code == 200

    wrong_current = await client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "WrongPass1!", "new_password": "NewStrongPass2!"},
    )
    assert wrong_current.status_code == 401
    assert (await client.get("/api/v1/auth/me")).status_code == 200

    changed = await client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "StrongPass1!", "new_password": "NewStrongPass2!"},
    )
    assert changed.status_code == 200
    assert not session_repository.sessions
    assert (await client.get("/api/v1/auth/me")).status_code == 401

    old_login = await client.post(
        "/api/v1/auth/login",
        json={"username": "alice", "password": "StrongPass1!"},
    )
    assert old_login.status_code == 401

    new_login = await client.post(
        "/api/v1/auth/login",
        json={"username": "alice", "password": "NewStrongPass2!"},
    )
    assert new_login.status_code == 200


async def test_deactivate_account_revokes_sessions_and_blocks_login(client: AsyncClient) -> None:
    assert (await register(client)).status_code == 201
    assert (
        await client.post(
            "/api/v1/auth/login",
            json={"username": "alice", "password": "StrongPass1!"},
        )
    ).status_code == 200

    wrong_password = await client.post("/api/v1/auth/deactivate", json={"password": "WrongPass1!"})
    assert wrong_password.status_code == 401

    deactivated = await client.post("/api/v1/auth/deactivate", json={"password": "StrongPass1!"})
    assert deactivated.status_code == 200
    assert (await client.get("/api/v1/auth/me")).status_code == 401

    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "alice", "password": "StrongPass1!"},
    )
    assert login.status_code == 401

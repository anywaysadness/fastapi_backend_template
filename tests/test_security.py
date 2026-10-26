from uuid import uuid4

import pytest

from src.domains.auth.exceptions import InvalidTokenError
from src.infrastructure.auth import Argon2PasswordHasher, JwtService


def test_password_hasher_uses_pepper() -> None:
    first = Argon2PasswordHasher(pepper="pepper-one", time_cost=1, memory_cost=8192, parallelism=1)
    second = Argon2PasswordHasher(pepper="pepper-two", time_cost=1, memory_cost=8192, parallelism=1)
    hashed = first.hash("secret-password")

    assert first.verify("secret-password", hashed)
    assert not first.verify("wrong-password", hashed)
    assert not second.verify("secret-password", hashed)
    first.verify_dummy("secret-password")


def test_jwt_contains_revocable_session_id() -> None:
    service = JwtService(
        secret_key="x" * 32,
        expire_minutes=5,
        issuer="test-issuer",
        audience="test-audience",
    )
    session_id = uuid4()
    token = service.create_access_token(42, session_id)
    payload = service.decode(token)

    assert payload["sub"] == "42"
    assert payload["jti"] == str(session_id)
    assert payload["type"] == "access"
    assert payload["iss"] == "test-issuer"
    assert payload["aud"] == "test-audience"
    service.validate_type(payload, "access")

    with pytest.raises(InvalidTokenError):
        service.validate_type(payload, "refresh")
    with pytest.raises(InvalidTokenError):
        service.decode(token + "tampered")


def test_jwt_rejects_wrong_issuer_or_audience() -> None:
    token = JwtService(secret_key="x" * 32, issuer="issuer-a", audience="audience-a").create_access_token(1, uuid4())
    other = JwtService(secret_key="x" * 32, issuer="issuer-b", audience="audience-b")

    with pytest.raises(InvalidTokenError):
        other.decode(token)

from datetime import UTC, datetime, timedelta

import pytest

from src.domains.auth.entities import Session
from src.domains.auth.exceptions import InvalidPasswordError
from src.domains.auth.value_objects import PasswordVO
from src.domains.users.exceptions import InvalidEmailError, InvalidUsernameError
from src.domains.users.value_objects import EmailVO, UsernameVO


def test_username_is_normalized() -> None:
    assert UsernameVO("  Alice_01 ").value == "alice_01"


@pytest.mark.parametrize("value", ["ab", "bad name", "юзер", "a" * 129])
def test_invalid_username_is_rejected(value: str) -> None:
    with pytest.raises(InvalidUsernameError):
        UsernameVO(value)


def test_email_is_normalized() -> None:
    assert EmailVO("  Foo@Bar.com ").value == "foo@bar.com"


def test_invalid_email_is_rejected() -> None:
    with pytest.raises(InvalidEmailError):
        EmailVO("not-an-email")


def test_password_limits() -> None:
    assert PasswordVO("secret").value == "secret"
    with pytest.raises(InvalidPasswordError):
        PasswordVO("")
    with pytest.raises(InvalidPasswordError):
        PasswordVO("a" * 129)


def test_session_validity_and_revocation() -> None:
    session = Session.create(
        user_id=1,
        expires_at=datetime.now(UTC) + timedelta(minutes=5),
        user_agent="x" * 1000,
    )
    assert session.is_valid()
    assert len(session.user_agent or "") == 512

    session.revoke()
    assert not session.is_valid()

    restored = Session.from_dict(session.to_dict())
    assert not restored.is_valid()
    assert (
        Session.from_dict(
            Session.create(
                user_id=1,
                expires_at=datetime.now(UTC) - timedelta(seconds=1),
            ).to_dict()
        ).is_valid()
        is False
    )

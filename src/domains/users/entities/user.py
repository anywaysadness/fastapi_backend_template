from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Self

from src.domains.auth.value_objects import UsernameVO
from src.domains.users.value_objects import EmailVO


@dataclass
class UserEntity:
    id: int
    username: UsernameVO
    hashed_password: str
    created_at: datetime

    email: EmailVO | None = None
    is_active: bool = True
    is_admin: bool = False

    @classmethod
    def create(
        cls,
        username: UsernameVO,
        hashed_password: str,
        email: EmailVO | None = None,
        is_active: bool = True,
        is_admin: bool = False,
    ) -> Self:
        return cls(
            id=0,
            username=username,
            hashed_password=hashed_password,
            created_at=datetime.now(tz=UTC),
            email=email,
            is_active=is_active,
            is_admin=is_admin,
        )

    def deactivate(self) -> None:
        """Деактивация пользователя"""
        self.is_active = False

    def activate(self) -> None:
        """Активация пользователя"""
        self.is_active = True

    def change_email(self, email: EmailVO) -> None:
        """Изменение email пользователя"""
        self.email = email

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username.value,
            "hashed_password": self.hashed_password,
            "created_at": self.created_at,
            "email": self.email.value if self.email else None,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        id_ = data.get("id")
        username = UsernameVO(data["username"])
        hashed_password = data["hashed_password"]

        email_raw = data.get("email")
        email = EmailVO(email_raw) if email_raw is not None else None

        is_active = data.get("is_active", True)
        is_admin = data.get("is_admin", False)
        created_at = data.get("created_at")

        kwargs = {
            "id": id_,
            "username": username,
            "hashed_password": hashed_password,
            "email": email,
            "is_active": is_active,
            "is_admin": is_admin,
        }
        if created_at is not None:
            kwargs["created_at"] = created_at

        return cls(**kwargs)

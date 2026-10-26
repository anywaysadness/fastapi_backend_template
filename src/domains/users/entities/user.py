from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Self

from src.domains.users.value_objects import EmailVO, UsernameVO


@dataclass
class UserEntity:
    """Доменный пользователь с нормализованными username и email."""

    id: int | None
    username: UsernameVO
    hashed_password: str
    created_at: datetime
    updated_at: datetime | None = None
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
        """Создаёт нового активного пользователя."""
        now = datetime.now(tz=UTC)
        return cls(
            id=None,
            username=username,
            hashed_password=hashed_password,
            created_at=now,
            updated_at=now,
            email=email,
            is_active=is_active,
            is_admin=is_admin,
        )

    @property
    def is_new(self) -> bool:
        """Возвращает True, если пользователь ещё не сохранён."""
        return self.id is None

    def deactivate(self) -> None:
        """Деактивирует пользователя."""
        self.is_active = False
        self._touch()

    def activate(self) -> None:
        """Активирует пользователя."""
        self.is_active = True
        self._touch()

    def change_email(self, email: EmailVO) -> None:
        """Меняет email пользователя."""
        self.email = email
        self._touch()

    def change_password(self, hashed_password: str) -> None:
        """Заменяет хеш пароля."""
        self.hashed_password = hashed_password
        self._touch()

    def _touch(self) -> None:
        """Обновляет дату изменения."""
        self.updated_at = datetime.now(tz=UTC)

    def to_persistence(self) -> dict[str, Any]:
        """Возвращает whitelist-представление для сохранения в БД."""
        return {
            "id": self.id,
            "username": self.username.value,
            "hashed_password": self.hashed_password,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "email": self.email.value if self.email else None,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Восстанавливает сущность из строки БД."""
        email_raw = data.get("email")
        return cls(
            id=data.get("id"),
            username=UsernameVO(data["username"]),
            hashed_password=data["hashed_password"],
            created_at=data.get("created_at") or datetime.now(tz=UTC),
            updated_at=data.get("updated_at"),
            email=EmailVO(email_raw) if email_raw is not None else None,
            is_active=data.get("is_active", True),
            is_admin=data.get("is_admin", False),
        )

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Self

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

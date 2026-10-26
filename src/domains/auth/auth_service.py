from src.domains.auth.exceptions import InvalidCredentialsError
from src.domains.auth.interfaces import PasswordHasher
from src.domains.auth.value_objects.password import PasswordVO
from src.domains.users.entities.user import UserEntity


class AuthService:
    """Проверяет учётные данные без знания о HTTP, JWT и Redis."""

    def __init__(self, password_hasher: PasswordHasher) -> None:
        """Сохраняет порт для проверки пароля."""
        self._password_hasher = password_hasher

    def verify_credentials(self, user: UserEntity | None, plain_password: PasswordVO) -> UserEntity:
        """Возвращает активного пользователя или выбрасывает ошибку входа."""
        if user is None:
            self._password_hasher.verify_dummy(plain_password.value)
            raise InvalidCredentialsError()

        password_is_valid = self._password_hasher.verify(plain_password.value, user.hashed_password)
        if not user.is_active or not password_is_valid:
            raise InvalidCredentialsError()

        return user

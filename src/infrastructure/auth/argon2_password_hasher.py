import hashlib
import hmac

from argon2 import PasswordHasher as Argon2PasswordHasherCore
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from src.domains.auth.interfaces import PasswordHasher


class Argon2PasswordHasher(PasswordHasher):
    """Argon2id-адаптер с опциональным HMAC-pepper."""

    def __init__(
        self,
        pepper: str = "",
        *,
        time_cost: int = 3,
        memory_cost: int = 65536,
        parallelism: int = 4,
    ) -> None:
        """Настраивает параметры Argon2 и dummy-хеш."""
        self._pepper = pepper.encode()
        self._hasher = Argon2PasswordHasherCore(
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
        )
        self._dummy_hash = self._hasher.hash(self._season("dummy-password"))

    def hash(self, raw_password: str) -> str:
        """Хеширует пароль после применения pepper."""
        return self._hasher.hash(self._season(raw_password))

    def verify(self, raw_password: str, hashed_password: str) -> bool:
        """Проверяет пароль и возвращает False для битого хеша."""
        try:
            return self._hasher.verify(hashed_password, self._season(raw_password))
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False

    def verify_dummy(self, raw_password: str) -> None:
        """Выполняет проверку по dummy-хешу для выравнивания времени."""
        self.verify(raw_password, self._dummy_hash)

    def _season(self, raw_password: str) -> str:
        """Добавляет к паролю HMAC-pepper, если он задан."""
        if not self._pepper:
            return raw_password
        return hmac.new(self._pepper, raw_password.encode(), hashlib.sha256).hexdigest()

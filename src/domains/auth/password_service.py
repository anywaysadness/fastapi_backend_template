# src/domains/auth/services/password_service.py
import hmac

import bcrypt


class PasswordService:
    def __init__(self, secret_key: str, hmac_digest: str = "sha256", encoding: str = "utf-8") -> None:
        self._secret_key = secret_key.encode(encoding)
        self._hmac_digest = hmac_digest
        self._encoding = encoding

    def hash(self, password: str) -> str:
        salt = bcrypt.gensalt()
        peppered = self._pepper(password, salt)
        return bcrypt.hashpw(peppered, salt).decode(self._encoding)

    def verify(self, plain: str, hashed: str) -> bool:
        salt = hashed[:29].encode(self._encoding)
        peppered = self._pepper(plain, salt)
        return bcrypt.checkpw(peppered, hashed.encode(self._encoding))

    def _pepper(self, password: str, salt: bytes) -> bytes:
        seasoned = hmac.new(self._secret_key, msg=password.encode(self._encoding), digestmod=self._hmac_digest)
        seasoned.update(salt)
        return seasoned.digest()

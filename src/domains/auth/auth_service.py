import logging

from src.domains.auth.exceptions import InvalidCredentialsError
from src.domains.auth.password_service import PasswordService
from src.domains.auth.value_objects.password import PasswordVO
from src.domains.users.entities.user import UserEntity

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, password_service: PasswordService):
        self._password_service = password_service

    def verify_credentials(self, user: UserEntity | None, plain_password: PasswordVO) -> None:
        if user is None or not self._password_service.verify(plain_password.value, user.hashed_password):
            raise InvalidCredentialsError()

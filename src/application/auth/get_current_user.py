from uuid import UUID

from src.domains.auth.exceptions import InvalidTokenError
from src.domains.auth.interfaces import TokenService
from src.domains.auth.services import SessionService
from src.domains.uow import UnitOfWork
from src.domains.users.entities import UserEntity
from src.domains.users.services import UserService


class GetCurrentUserUseCase:
    """Сценарий получения текущего пользователя."""

    def __init__(
        self,
        uow: UnitOfWork,
        token_service: TokenService,
        user_service: UserService,
        session_service: SessionService,
    ) -> None:
        """Сохраняет зависимости сценария."""
        self._uow = uow
        self._token_service = token_service
        self._user_service = user_service
        self._session_service = session_service

    async def execute(self, token: str) -> UserEntity:
        """Проверяет JWT, сессию и активность пользователя."""
        payload = self._token_service.decode(token)
        self._token_service.validate_type(payload, "access")

        try:
            user_id = int(str(payload["sub"]))
            session_id = UUID(str(payload["jti"]))
        except (KeyError, TypeError, ValueError) as exc:
            raise InvalidTokenError() from exc

        session = await self._session_service.get_by_id(session_id)
        if session is None or session.user_id != user_id:
            raise InvalidTokenError()

        async with self._uow:
            user = await self._user_service.get_by_id(user_id)

        if user is None or not user.is_active:
            raise InvalidTokenError()

        return user

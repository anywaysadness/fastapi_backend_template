from uuid import UUID

from src.common.base_exception import BaseDomainException
from src.domains.auth.interfaces import SessionRepository, TokenService


class LogoutUserUseCase:
    """Сценарий выхода пользователя."""

    def __init__(self, token_service: TokenService, session_repository: SessionRepository) -> None:
        """Сохраняет зависимости сценария."""
        self._token_service = token_service
        self._session_repository = session_repository

    async def execute(self, token: str | None) -> None:
        """Отзывает текущую серверную сессию, если токен валиден."""
        if not token:
            return

        try:
            payload = self._token_service.decode(token)
            self._token_service.validate_type(payload, "access")
            session_id = UUID(str(payload["jti"]))
        except (BaseDomainException, KeyError, TypeError, ValueError):
            return

        await self._session_repository.revoke_by_id(session_id)

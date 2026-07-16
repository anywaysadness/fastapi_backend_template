from collections.abc import Callable

from src.application.users.dto import AuthResult
from src.common.configuration import conf
from src.domains.auth.auth_service import AuthService
from src.domains.auth.value_objects import PasswordVO, UsernameVO
from src.infrastructure.auth.jwt_service import JwtService
from src.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from src.presentation.user.schemas import BaseUserSchema


class UserAuthUseCase:
    def __init__(
        self,
        session_factory: Callable,
        auth_service: AuthService,
        jwt_service: JwtService,
    ) -> None:
        self._session_factory = session_factory
        self._auth_service = auth_service
        self._jwt_service = jwt_service

    async def user_authentication(self, user_data: BaseUserSchema) -> AuthResult:
        """Авторизация пользователя"""
        username = UsernameVO(user_data.username)
        password = PasswordVO(user_data.password)

        async with SqlAlchemyUnitOfWork(self._session_factory) as uow:
            user = await uow.users.find_by_username(username)
            self._auth_service.verify_credentials(user, password)

        access_token = self._jwt_service.create_access_token(user.id, conf.jwt_auth.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token = self._jwt_service.create_refresh_token(user.id, conf.jwt_auth.REFRESH_TOKEN_EXPIRE_DAYS)

        return AuthResult(
            user=user,
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_max_age=conf.jwt_auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_token_max_age=conf.jwt_auth.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        )

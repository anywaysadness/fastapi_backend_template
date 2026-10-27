from fastapi import Depends

from src.di.common import get_uow
from src.domains.uow import UnitOfWork
from src.domains.users.services import UserService


def get_user_service(uow: UnitOfWork = Depends(get_uow)) -> UserService:
    """Собирает сервис пользователей для текущего запроса."""
    return UserService(uow=uow)

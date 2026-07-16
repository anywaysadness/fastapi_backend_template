from typing import Protocol

from src.domains.auth.value_objects.username import UsernameVO
from src.domains.users.entities import UserEntity


class UserRepositoryProtocol(Protocol):
    async def save(self, user: UserEntity) -> UserEntity: ...
    async def get_by_id(self, user_id: int) -> UserEntity: ...
    async def find_by_username(self, username: UsernameVO) -> UserEntity | None: ...

from src.domains.users.repositories import UserRepository
from src.domains.users.services import UserService


def user_service():
    return UserService(UserRepository())

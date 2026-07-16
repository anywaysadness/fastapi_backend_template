from dataclasses import dataclass

from src.domains.auth.value_objects import PasswordVO, UsernameVO


@dataclass
class AuthUserData:
    username: UsernameVO
    password: PasswordVO

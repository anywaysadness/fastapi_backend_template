from fastapi import HTTPException


class UserNotAuthorizedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Пользователь не авторизован")


class InvalidTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Невалидный токен")


AUTH_EXEPTIONS: tuple = (
    UserNotAuthorizedException,
    InvalidTokenException,
)

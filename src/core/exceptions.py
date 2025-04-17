from fastapi import HTTPException, status


class InvalidTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Токен не валиден")


class InvalidCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Неверное имя пользователя или пароль")


class UserAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="Пользователь уже существует")


class UserDoesNotExist(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="Пользователь не существует")


class UserNotActiveException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Пользователь не активен")


class UserNotAdminException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Недостаточно прав для выполнения")


class UserNotAuthorizedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Пользователь не авторизован")


class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Пользователь не найден")


AUTH_EXEPTIONS: tuple = (
    InvalidTokenException,
    InvalidCredentialsException,
    UserAlreadyExistsException,
    UserDoesNotExist,
    UserNotActiveException,
    UserNotAdminException,
    UserNotAuthorizedException,
    UserNotFoundException,
)

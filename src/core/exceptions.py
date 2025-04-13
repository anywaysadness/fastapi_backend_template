from fastapi import HTTPException, status


class InvalidTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Не валидный токен")


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
        super().__init__(status_code=403, detail="Аккаунт не активен")


class UserNotAdminException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Недостаточно прав. Пользователь не админ")


class UserNotAuthorizedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Пользователь не авторизован")


class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Не найден пользователь")


AUTH_EXEPTIONS: tuple = (
    UserNotAdminException,
    UserNotActiveException,
    UserNotAuthorizedException,
    InvalidTokenException,
)

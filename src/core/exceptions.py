from fastapi import HTTPException, status


class InvalidTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Не валидный токен")


class UserAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="Пользователь не существует")


class UserNotAuthorizedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Пользователь не авторизован")


class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Не найден пользователь")

from fastapi import Response

from src.common.configuration import conf


def set_auth_cookie(response: Response, token: str, max_age: int) -> None:
    """Устанавливает HttpOnly cookie с access-токеном."""
    response.set_cookie(
        key=conf.app.AUTH_COOKIE_NAME,
        value=token,
        max_age=max_age,
        path="/",
        domain=conf.app.COOKIE_DOMAIN,
        httponly=True,
        secure=conf.app.COOKIE_SECURE,
        samesite=conf.app.COOKIE_SAMESITE,
    )


def clear_auth_cookie(response: Response) -> None:
    """Удаляет cookie с access-токеном."""
    response.delete_cookie(
        key=conf.app.AUTH_COOKIE_NAME,
        path="/",
        domain=conf.app.COOKIE_DOMAIN,
    )

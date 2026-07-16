from fastapi import Response, Security
from fastapi.security import APIKeyCookie

from src.common.exceptions import UserNotAuthorizedException
from src.infrastructure.auth.jwt_service import JwtService


def create_cookie_scheme(cookie_name: str) -> APIKeyCookie:
    return APIKeyCookie(name=cookie_name, auto_error=False)


def set_token_cookie(response: Response, key: str, value: str, max_age: int) -> None:
    response.set_cookie(key=key, value=value, httponly=True, secure=True, samesite="lax", max_age=max_age)


def get_token_payload_dependency(scheme: APIKeyCookie, jwt_service: JwtService, token_type: str):
    async def dependency(token: str = Security(scheme)) -> dict:
        if not token:
            raise UserNotAuthorizedException
        payload = jwt_service.decode(token)
        jwt_service.validate_type(payload, token_type)
        return payload

    return dependency

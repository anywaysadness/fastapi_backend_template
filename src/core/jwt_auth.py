import logging
from datetime import UTC, datetime, timedelta

import bcrypt
from fastapi import Depends, Response, Security
from fastapi.security import APIKeyCookie
from jose import JWTError, jwt
from jwt import InvalidTokenError

from src.core.configuration import conf
from src.core.exceptions import InvalidTokenException, UserNotAuthorizedException

logger = logging.getLogger(__name__)
auth_scheme_access_token = APIKeyCookie(
    name=conf.jwt_auth.ACCESS_TOKEN_TYPE + conf.jwt_auth.COOKIE_KEY, auto_error=False
)
auth_scheme_refresh_token = APIKeyCookie(
    name=conf.jwt_auth.REFRESH_TOKEN_TYPE + conf.jwt_auth.COOKIE_KEY, auto_error=False
)

# http_bearer = HTTPBearer(auto_error=False)
# oauth2_schema = OAuth2PasswordBearer(tokenUrl=f"/{conf.app_conf.get_app_settings()['prefix']}/auth/login/")


def get_hash_password(password: str) -> bytes:
    """Возвращает захэшированный пароль"""
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    hashed_bytes: bytes = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_bytes.decode("utf-8")


def verify_password(password: str, hashed_password: bytes) -> bool:
    """Проверяет соотвествие строки хэшу"""
    return bcrypt.checkpw(password=password.encode(), hashed_password=hashed_password)


def validate_token_type(payload: dict, token_type: str) -> bool:
    if payload.get(conf.jwt_auth.TOKEN_TYPE_FIELD) == token_type:
        return True
    raise InvalidTokenException


def create_token(user_id: int, token_type: str = conf.jwt_auth.ACCESS_TOKEN_TYPE) -> str:
    """Создает токен для пользователя"""
    payload = {"sub": str(user_id)}
    if token_type == conf.jwt_auth.ACCESS_TOKEN_TYPE:
        token = create_jwt(
            token_type=token_type,
            token_data=payload,
            expire_minutes=conf.jwt_auth.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
    elif token_type == conf.jwt_auth.REFRESH_TOKEN_TYPE:
        token = create_jwt(
            token_type=token_type,
            token_data=payload,
            expire_timedelta=timedelta(days=conf.jwt_auth.REFRESH_TOKEN_EXPIRE_DAYS),
        )
    return token



def decode_jwt(token: str, key: str = conf.jwt_auth.SECRET_KEY, algorithm: str = conf.jwt_auth.ALGORITHM):
    """Декодирует JWT-токен и возвращает данные"""
    try:
        decoded = jwt.decode(token=token, key=key, algorithms=[algorithm], options={"verify_exp": True})
        return decoded
    except JWTError:
        raise InvalidTokenException


def create_jwt(
    token_type: str,
    token_data: dict,
    expire_minutes: int = conf.jwt_auth.ACCESS_TOKEN_EXPIRE_MINUTES,
    expire_timedelta: timedelta | None = None,
) -> str:
    jwt_payload = {conf.jwt_auth.TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    jwt_token = encode_jwt(payload=jwt_payload, expire_minutes=expire_minutes, expire_timedelta=expire_timedelta)
    return jwt_token


def encode_jwt(
    payload: dict,
    key: str = conf.jwt_auth.SECRET_KEY,
    algorithm: str = conf.jwt_auth.ALGORITHM,
    expire_minutes: int = conf.jwt_auth.ACCESS_TOKEN_EXPIRE_MINUTES,
    expire_timedelta: timedelta | None = None,
):
    """Создание JWT токена доступа"""
    to_encode = payload.copy()
    now = datetime.now(UTC)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)

    to_encode.update(exp=int(expire.timestamp()), iat=int(now.timestamp()))
    encoded_jwt = jwt.encode(to_encode, key=key, algorithm=algorithm)
    return encoded_jwt


def set_token_in_cookie(
    response: Response,
    token: str,
    token_type: str = conf.jwt_auth.ACCESS_TOKEN_TYPE,
    expire_minutes: int = conf.jwt_auth.ACCESS_TOKEN_EXPIRE_MINUTES,
    expire_timedelta: timedelta | None = None,
):
    """Установка токена в куки"""

    if expire_timedelta:
        max_age = int(expire_timedelta.total_seconds())
    else:
        max_age = expire_minutes * 60

    response.set_cookie(
        key=token_type + conf.jwt_auth.COOKIE_KEY,
        value=token,
        httponly=True,  # Защита от доступа через JavaScript
        secure=True,  # Кука будет отправляться только по HTTPS
        samesite="lax",  # Защита от CSRF
        max_age=max_age,
    )


def get_token_payload_dependency(token_type: str):
    """Фабрика для создания зависимости get_token_payload"""
    if token_type == conf.jwt_auth.ACCESS_TOKEN_TYPE:
        scheme = auth_scheme_access_token
    elif token_type == conf.jwt_auth.REFRESH_TOKEN_TYPE:
        scheme = auth_scheme_refresh_token
    else:
        raise ValueError(f"Неизвестный тип токена: {token_type}")

    def get_token_payload(token: str = Security(scheme)) -> dict:
        """Возвращает payload для указанного типа токена"""
        if not token or not isinstance(token, str):
            raise UserNotAuthorizedException
        try:
            payload = decode_jwt(token=token)
            validate_token_type(payload=payload, token_type=token_type)
            return payload
        except InvalidTokenError:
            raise InvalidTokenException

    return get_token_payload
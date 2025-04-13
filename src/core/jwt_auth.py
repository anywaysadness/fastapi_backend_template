from datetime import UTC, datetime, timedelta

import bcrypt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from jwt import InvalidTokenError

from src.core.configuration import conf
from src.core.exceptions import InvalidTokenException

oauth2_schema = OAuth2PasswordBearer(tokenUrl=f"/{conf.app_conf.get_app_settings()['prefix']}/auth/login/")


def hash_password(password: str) -> bytes:
    """Возвращает захэшированный пароль"""
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    hashed_bytes: bytes = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_bytes.decode("utf-8")


def verify_password(password: str, hashed_password: bytes) -> bool:
    """Проверяет соотвествие строки хэшу"""
    return bcrypt.checkpw(password=password.encode(), hashed_password=hashed_password)


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

    to_encode.update(exp=expire, iat=now)
    encoded_jwt = jwt.encode(to_encode, key, algorithm=algorithm)
    return encoded_jwt


def decode_jwt(token: str, key: str = conf.jwt_auth.SECRET_KEY, algorithm: str = conf.jwt_auth.ALGORITHM):
    """Декодирует JWT-токен и возвращает данные"""
    try:
        decoded = jwt.decode(token, key, algorithms=[algorithm])
        return decoded
    except JWTError:
        raise InvalidTokenException


def get_current_token_payload(access_token: str = Depends(oauth2_schema)):
    """Возвращает тело токена"""
    try:
        payload = decode_jwt(token=access_token)
        return payload
    except InvalidTokenError:
        raise InvalidTokenException


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    """Создание JWT токена обновления"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(days=conf.jwt_auth.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, conf.jwt_auth.SECRET_KEY, algorithm=conf.jwt_auth.ALGORITHM)

from src.core.base_schemas import BaseSchema


class TokenInfo(BaseSchema):
    access_token: str
    refresh_token: str | None = None

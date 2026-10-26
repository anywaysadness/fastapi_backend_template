from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Базовая схема с запретом неизвестных полей."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class ResponseSchema(BaseSchema):
    """Универсальный ответ с текстовым сообщением."""

    message: str

from pydantic import BaseModel


class BaseSchema(BaseModel):
    class Config:
        from_attributes = True


class ResponseSchema(BaseSchema):
    message: str

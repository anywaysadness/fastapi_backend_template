import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.common.base_exception import BaseDomainException

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрирует единые обработчики ошибок приложения."""

    @app.exception_handler(BaseDomainException)
    async def domain_exception_handler(request: Request, exc: BaseDomainException) -> JSONResponse:
        """Преобразует доменное исключение в JSON-ответ."""
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Отдаёт ошибки валидации без исходных значений полей."""
        errors = [
            {
                "loc": list(error.get("loc", ())),
                "msg": error.get("msg", "Invalid value"),
                "type": error.get("type", "value_error"),
            }
            for error in exc.errors()
        ]
        return JSONResponse(status_code=422, content={"detail": errors})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Логирует неожиданную ошибку и скрывает детали от клиента."""
        logger.exception("Unhandled error while processing %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content={"detail": "Внутренняя ошибка сервера"})

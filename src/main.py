import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

from src.common.configuration import conf
from src.common.exception_handlers import register_exception_handlers
from src.common.logging_conf import configure_logging
from src.infrastructure.database.connection import check_database, close_database, migrate
from src.infrastructure.startup import run_startup_tasks
from src.routers import all_routers

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управляет ресурсами приложения и startup-миграциями."""
    configure_logging(conf.app.LOG_LEVEL)
    redis_client = Redis.from_url(
        conf.redis.build_connection_str_for_redis(),
        decode_responses=True,
    )
    app.state.redis = redis_client

    try:
        await run_startup_tasks([("alembic_upgrade", migrate)])
        logger.info("Application started in '%s' mode", conf.app.ENV)
        yield
    finally:
        await redis_client.aclose()
        await close_database()
        logger.info("Application stopped")


def create_app() -> FastAPI:
    """Создаёт и настраивает FastAPI-приложение."""
    show_docs = conf.app.is_development
    app = FastAPI(
        title="Template API",
        description=(
            "Шаблон backend-приложения с DDD-слоями, асинхронным SQLAlchemy, "
            "отзываемыми JWT-сессиями в Redis и rate limiting."
        ),
        openapi_url="/api/openapi.json" if show_docs else None,
        docs_url="/api/docs" if show_docs else None,
        redoc_url="/api/redoc" if show_docs else None,
        openapi_tags=[
            {
                "name": "auth",
                "description": "Вход, выход, текущий пользователь и управление аккаунтом.",
            },
            {
                "name": "users",
                "description": "Регистрация пользователей.",
            },
        ],
        lifespan=lifespan,
    )

    if conf.app.CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=conf.app.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization"],
        )

    register_exception_handlers(app)

    for router in all_routers:
        app.include_router(router)

    @app.get("/health/live", include_in_schema=False)
    async def health_live() -> dict[str, str]:
        """Возвращает liveness-статус приложения."""
        return {"status": "ok"}

    @app.get("/health/ready", include_in_schema=False)
    async def health_ready(request: Request) -> JSONResponse:
        """Проверяет доступность PostgreSQL и Redis."""
        try:
            await check_database()
            redis_client: Redis = request.app.state.redis
            await redis_client.ping()
        except Exception:
            logger.warning("Readiness check failed", exc_info=True)
            return JSONResponse(status_code=503, content={"status": "unavailable"})
        return JSONResponse(content={"status": "ok"})

    return app


app = create_app()

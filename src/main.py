import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from src.common.configuration import conf
from src.common.logging_conf import configure_logging
from src.infrastructure.database.connection import migrate
from src.routers import all_routers

logger = logging.getLogger(__name__)

app_settings = conf.app.get_app_settings()


# Жизненный цикл приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(level=app_settings["log_level"])
    await migrate()
    logger.info(f"Приложение запущено в '{conf.app.ENV}' режиме")
    yield
    logger.info("Приложение завершено")


# Настройки маршрутизации

api_router = APIRouter(
    prefix=f"/{app_settings['prefix']}",
    responses={404: {"description": "Page not found"}},
)

# Создание экземпляра FastAPI
app = FastAPI(
    title="Template API",
    openapi_url=f"/{app_settings['prefix']}/openapi.json" if app_settings["enable_dev"] else None,
    docs_url=f"/{app_settings['prefix']}/docs" if app_settings["enable_dev"] else None,
    redoc_url=f"/{app_settings['prefix']}/redoc" if app_settings["enable_dev"] else None,
    lifespan=lifespan,
)


# Регистрация роутеров
for router in all_routers:
    api_router.include_router(router)

app.include_router(api_router)

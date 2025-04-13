import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from src.core.configuration import conf
from src.routers import all_routers

logger = logging.getLogger(__name__)


# Жизненный цикл приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup completed")
    yield
    logger.info("Shutdown completed")


# Настройки маршрутизации
app_settings = conf.app_conf.get_app_settings()
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

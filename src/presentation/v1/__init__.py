from fastapi import APIRouter

from src.presentation.v1.auth.router import auth_router
from src.presentation.v1.users.router import users_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(users_router)

__all__ = ["api_router"]

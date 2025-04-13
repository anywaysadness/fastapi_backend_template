from src.domains.auth.routers import auth_router
from src.domains.users.routers import user_router

all_routers = [auth_router, user_router]

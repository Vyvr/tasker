from fastapi import FastAPI

from app.core.logging_config import setup_loggers
from app.middleware.logging_middleware import LoggingMiddleware
from app.routes.users import router as users_router
from app.routes.teams import router as teams_router
from app.routes.tasks import router as tasks_router
from app.routes.projects import router as projects_router

setup_loggers()

app = FastAPI()

app.add_middleware(LoggingMiddleware)
app.include_router(users_router)
app.include_router(teams_router)
app.include_router(tasks_router)
app.include_router(projects_router)

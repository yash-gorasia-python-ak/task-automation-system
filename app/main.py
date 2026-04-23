from fastapi import FastAPI, Request
from app.db.base import Base
from app.db.session import engine
from contextlib import asynccontextmanager
from app.error.register_handlers import register_all_error
from app.middleware.log_middleware import RequestLoggingMiddleware
from app.api import auth
from app.api import task

from app.models import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.add_middleware(RequestLoggingMiddleware)

@app.middleware("http")
async def dispatch(request: Request, call_next):

    try:
        response = await call_next(request)
        return response

    except Exception as exc:
        handler = app.exception_handlers.get(Exception)
        return await handler(request, exc)


register_all_error(app)

app.include_router(auth.auth_router, prefix="/auth", tags=["Auth Endpoints"])
app.include_router(task.task_router, prefix="/tasks", tags=["Task Endpoints"])

from fastapi import FastAPI, Request
from app.db.base import Base
from app.db.session import engine
from contextlib import asynccontextmanager
from app.error.register_handlers import register_all_error
from app.api import auth
from app.api import task

from app.models.task_model import Task
from app.models.user_model import User


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


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

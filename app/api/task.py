from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.current_user import get_current_user
from app.dependencies.get_session import get_db

from app.services.schedule import create_dynamic_task
from app.schemas.task_schema import TaskCreate
from app.schemas.token_schema import TokenData

task_router = APIRouter()

@task_router.post("/")
async def create_task(paylaod: TaskCreate, user: Annotated[TokenData, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):

    return await create_dynamic_task(paylaod, user.user_id, db)

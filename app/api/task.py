from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.current_user import get_current_user
from app.dependencies.get_session import get_db
from app.dependencies.rbac import RoleChecker

from app.services.schedule import create_dynamic_task
from app.services.task_get_del_service import TaskGetDelService

from app.schemas.task_schema import TaskCreate
from app.schemas.token_schema import TokenData


current_user = Annotated[TokenData, Depends(RoleChecker(["user"]))]

task_router = APIRouter()

@task_router.post("/")
async def create_task(paylaod: TaskCreate, user: Annotated[TokenData, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):

    return await create_dynamic_task(paylaod, user.user_id, db)

@task_router.get("/")
async def get_all_tasks(user: Annotated[TokenData, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):

    return await TaskGetDelService(db).get_tasks(user.user_id)

@task_router.get("/{task_id}")
async def get_task_id(task_id: int, user: Annotated[TokenData, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):

    return await TaskGetDelService(db).get_task_by_id(task_id)


@task_router.delete("/{task_id}")
async def delete_task(task_id: int, user: Annotated[TokenData, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):

    return await TaskGetDelService(db).delete_task_id(task_id)

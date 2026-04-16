from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.get_session import get_db
from app.dependencies.rbac import RoleChecker
from app.schemas.user_schema import RegisterRequest
from app.services.admin_service import AdminService
from app.schemas.token_schema import TokenData

current_user = Annotated[TokenData, Depends(RoleChecker(["admin", "user"]))]

admin_router = APIRouter()

"""
current user err
"""
@admin_router.post("/trigger/{task_id}")
async def trigger_task_now(
    task_id: int,
    current_user: current_user,
    db: Annotated[AsyncSession, Depends(get_db)],
):

    return await AdminService(db).trigger(task_id)

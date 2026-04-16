from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.task_model import Task
from sqlalchemy_celery_beat import PeriodicTask


class TaskRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_tasks_db(self, user_id):
        res = await self.db.execute(select(Task).where(Task.user_id == user_id))
        return res.scalars().all()

    async def get_task_id_db(self, task_id):
        res = await self.db.execute(select(Task).where(Task.task_id == task_id))
        return res.scalar_one_or_none()

    async def delete_task_db(self, task_id):
        await self.db.execute(delete(Task).where(Task.task_id == task_id))
        await self.db.execute(
            delete(PeriodicTask).where(PeriodicTask.name.like(f"%-Task-{task_id}"))
        )
        await self.db.commit()

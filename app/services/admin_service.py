from sqlalchemy.ext.asyncio import AsyncSession
from app.queue.celery import celery_app
from app.repositories.task_repository import TaskRepository
from app.error.custom_execption import TaskNotFound


class AdminService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = TaskRepository(db)

    async def trigger(self, task_id):
        async with self.db.begin_nested():
            task = await self.repo.get_task_id_db(task_id)
            if not task:
                raise TaskNotFound()

        celery_app.send_task(
            name=task.task_type.value,
            args=[task.user_id, task_id],
        )

        return {"message": f"Manual trigger sent for task: {task.name}"}

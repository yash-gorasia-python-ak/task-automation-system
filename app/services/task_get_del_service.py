from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.task_repository import TaskRepository
from app.error.custom_execption import TaskNotFound


class TaskGetDelService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = TaskRepository(db)

    async def get_tasks(self, user_id):
        async with self.db.begin_nested():
            tasks = await self.repo.get_tasks_db(user_id)

            return tasks

    async def get_task_by_id(self, task_id):
        async with self.db.begin_nested():
            task = await self.repo.get_task_id_db(task_id)

            if not task:
                raise TaskNotFound()

            return task

    async def delete_task_id(self, task_id):
        async with self.db.begin_nested():
            task = await self.repo.get_task_id_db(task_id)

            if not task:
                raise TaskNotFound()

            await self.repo.delete_task_db(task_id)

            return {"message": f"{task_id} deleted successfully"}

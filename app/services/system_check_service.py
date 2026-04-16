import shutil
from datetime import datetime, timezone
from sqlalchemy import select
from app.models.task_model import Task
from app.schemas.task_schema import TaskStatus


async def system_check(user_id, task_id, db):
    res = await db.execute(select(Task).where(Task.task_id == task_id))
    task = res.scalar_one_or_none()

    if not task:
        return

    usage = shutil.disk_usage("/")

    total_gb = usage.total / (1024**3)
    used_gb = usage.used / (1024**3)

    disk_info = f"used: {used_gb} GB, total: {total_gb} GB"

    task.status = TaskStatus.COMPLETED
    task.last_run_at = datetime.now(timezone.utc)
    task.description = f"Last system_check: {disk_info}"

    await db.commit()

    print(f"system_check for {user_id}: {disk_info}")

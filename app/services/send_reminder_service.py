from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.user_model import User
from app.models.task_model import Task
from app.schemas.task_schema import TaskStatus
from datetime import datetime, timezone


async def send_reminder(user_id: int, task_id: int, db: AsyncSession, mail_client):
    user_res = await db.execute(select(User).where(User.user_id == user_id))
    task_res = await db.execute(select(Task).where(Task.task_id == task_id))

    user = user_res.scalar_one_or_none()
    task = task_res.scalar_one_or_none()

    if not user or not task:
        return

    task.status = TaskStatus.RUNNING
    await db.commit()

    try:
        from app.utils.mail_utils.mail import create_message

        message = create_message(
            recipients=[user.email],
            subject=f"Reminder: {task.name}",
            body=f"Don't forget: {task.description}",
        )
        await mail_client.send_message(message)

        task.status = TaskStatus.COMPLETED
        task.last_run_at = datetime.now(timezone.utc)
        await db.commit()

    except Exception as e:
        task.status = TaskStatus.FAILED
        await db.commit()
        raise e

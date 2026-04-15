from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.user_model import User
from app.models.task_model import Task
from app.schemas.task_schema import TaskStatus
from datetime import datetime, timezone

async def send_reminder(user_id: int, task_id: int, db: AsyncSession, mail_client):
    # 1. Fetch User and Task
    user_stmt = await db.execute(select(User).where(User.user_id == user_id))
    task_stmt = await db.execute(select(Task).where(Task.task_id == task_id))

    user = user_stmt.scalar_one_or_none()
    task = task_stmt.scalar_one_or_none()

    if not user or not task:
        return

    # 2. Update status to RUNNING
    task.status = TaskStatus.RUNNING
    await db.commit()

    try:
        # 3. Prepare and Send Email
        from app.utils.mail_utils.mail import create_message
        message = create_message(
            recipients=[user.email],
            subject=f"Reminder: {task.name}",
            body=f"Don't forget: {task.description}"
        )
        await mail_client.send_message(message)

        # 4. Success: Update status
        task.status = TaskStatus.COMPLETED
        task.last_run_at = datetime.now(timezone.utc)
        await db.commit()
        
    except Exception as e:
        task.status = TaskStatus.FAILED
        await db.commit()
        raise e

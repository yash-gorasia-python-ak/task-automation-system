import httpx
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.user_model import User
from app.models.task_model import Task
from app.schemas.task_schema import TaskStatus
from datetime import datetime, timezone


async def send_comic(user_id: int, task_id: int, db: AsyncSession, mail_client):
    user_stmt = await db.execute(select(User).where(User.user_id == user_id))
    task_stmt = await db.execute(select(Task).where(Task.task_id == task_id))

    user = user_stmt.scalar_one_or_none()
    task = task_stmt.scalar_one_or_none()

    if not user or not task:
        return

    task.status = TaskStatus.RUNNING
    await db.commit()

    try:
        async with httpx.AsyncClient() as client:
            random_id = random.randint(1, 3230)

            # Add 'info.0.json' to get the JSON metadata instead of the HTML page
            comic_res = await client.get(f"https://xkcd.com/{random_id}/info.0.json")

            comic_res.raise_for_status()
            comic_data = comic_res.json() # Now this will work!


        from app.utils.mail_utils.mail import create_message

        message = create_message(
            recipients=[user.email],
            subject=f"Fun Friday: {comic_data['title']}",
            body=f"Check out this comic: {comic_data['img']}\n\nAlt text: {comic_data['alt']}",
        )
        await mail_client.send_message(message)

        task.status = TaskStatus.COMPLETED
        task.last_run_at = datetime.now(timezone.utc)
        await db.commit()
        
    except Exception as e:
        task.status = TaskStatus.FAILED
        await db.commit()
        raise e

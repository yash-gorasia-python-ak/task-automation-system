import asyncio
from app.queue.celery import celery_app
from app.db.session import async_session
from app.utils.mail_utils.mail import mail
from app.services.send_reminder_service import send_reminder
from app.services.send_comic_service import send_comic
from app.services.system_check_service import system_check


@celery_app.task(name="reminder", bind=True, max_retries=3, default_retry_delay=60)
def send_scheduled_reminder(self, user_id: int, task_id: int):
    async def _run():
        async with async_session() as db:
            await send_reminder(user_id, task_id, db, mail)

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(_run())
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(name="system_check", bind=True, max_retries=3)
def system_check_in_intervals(self, user_id: int, task_id: int):
    async def _run():
        async with async_session() as db:
            await system_check(user_id, task_id, db)

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(_run())
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(name="send_comic", bind=True, max_retries=3, default_retry_delay=60)
def send_scheduled_comic(self, user_id: int, task_id: int):
    async def _run():
        async with async_session() as db:
            await send_comic(user_id, task_id, db, mail)

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(_run())
    except Exception as exc:
        raise self.retry(exc=exc)

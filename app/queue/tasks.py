import asyncio
from celery import Task
from app.queue.celery import celery_app
from app.db.session import async_session
from app.utils.mail_utils.mail import mail
from app.services.send_reminder_service import send_reminder
from app.services.send_comic_service import send_comic
from app.services.system_check_service import system_check


class AsyncDBTask(Task):
    _loop = None

    @property
    def loop(self):
        if self._loop is None or self._loop.is_closed():
            try:
                self._loop = asyncio.get_event_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        return self._loop

    def __call__(self, *args, **kwargs):
        async def _run_with_session():
            async with async_session() as db:
                kwargs["db"] = db
                return await self.run(*args, **kwargs)

            return self.loop.run_until_complete(_run_with_session())

@celery_app.task(
    base=AsyncDBTask,
    name="reminder",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
async def send_scheduled_reminder(self, user_id: int, task_id: int, db=None):
    await send_reminder(user_id, task_id, db, mail)


@celery_app.task(
    base=AsyncDBTask,
    name="system_check",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
async def system_check_in_intervals(self, user_id: int, task_id: int, db=None):
    await system_check(user_id, task_id, db)


@celery_app.task(
    base=AsyncDBTask,
    name="send_comic",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
async def send_scheduled_comic(self, user_id: int, task_id: int, db=None):
    await send_comic(user_id, task_id, db, mail)

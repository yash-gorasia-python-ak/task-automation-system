import json
from datetime import datetime, timezone
from app.models.task_model import Task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_celery_beat.models import (
    ClockedSchedule,
    CrontabSchedule,
    IntervalSchedule,
    PeriodicTask,
    PeriodicTaskChanged,
)
from app.schemas.task_schema import TaskType, TaskCreate


async def create_dynamic_task(data: TaskCreate, user_id: int, db: AsyncSession):
    new_task = Task(
        name=data.name,
        task_type=data.task_type,
        description=data.description,
        interval_time=data.interval_time,
        schedule_time=data.schedule_time,
        user_id=user_id,
    )
    db.add(new_task)
    await db.flush()

    schedule_id = None
    discriminator = ""

    if data.task_type == TaskType.REMINDER:
        dt = data.schedule_time
        sched = ClockedSchedule(clocked_time=dt)
        db.add(sched)
        await db.flush()
        schedule_id, discriminator = sched.id, "clockedschedule"

    elif data.task_type == TaskType.SYSTEM_CHECK:
        interval_seconds = max((int(data.interval_time) * 60), 60)

        sched = IntervalSchedule(every=interval_seconds, period="seconds")
        db.add(sched)
        await db.flush()
        schedule_id, discriminator = sched.id, "intervalschedule"

    elif data.task_type == TaskType.SEND_COMIC:
        dt = data.schedule_time

        sched = CrontabSchedule(
            minute=str(dt.minute),
            hour=str(dt.hour),
            day_of_month=str(dt.day),
            month_of_year=str(dt.month),
            day_of_week=dt.strftime("%w"),
        )
        db.add(sched)
        await db.flush()
        schedule_id, discriminator = sched.id, "crontabschedule"

    is_one_off = data.task_type == TaskType.REMINDER

    periodic_task = PeriodicTask(
        name=f"User-{user_id}-Task-{new_task.task_id}",
        task=data.task_type.value,
        schedule_id=schedule_id,
        discriminator=discriminator,
        args=json.dumps([user_id, new_task.task_id]),
        one_off=is_one_off,
        enabled=True,
    )
    db.add(periodic_task)

    await db.merge(PeriodicTaskChanged(id=1, last_update=datetime.now(timezone.utc)))
    await db.commit()

    return {"message": f"Task {new_task.name} scheduled successfully"}

import pytest
from sqlalchemy import select
from app.repositories.task_repository import TaskRepository
from app.models.task_model import Task
from app.models.user_model import User
from app.schemas.task_schema import TaskType
from sqlalchemy_celery_beat.models import PeriodicTask


@pytest.mark.asyncio
async def test_get_tasks_db_success(db_session):
    repo = TaskRepository(db_session)

    user = User(name="taskuser", email="t@t.com", password="p", role="user")
    db_session.add(user)
    await db_session.flush()

    task1 = Task(name="Task 1", user_id=user.user_id, task_type=TaskType.REMINDER)
    task2 = Task(name="Task 2", user_id=user.user_id, task_type=TaskType.SYSTEM_CHECK)
    db_session.add_all([task1, task2])
    await db_session.flush()

    tasks = await repo.get_tasks_db(user.user_id)

    assert len(tasks) == 2
    assert tasks[0].name in ["Task 1", "Task 2"]


@pytest.mark.asyncio
async def test_get_task_id_db_success(db_session):
    repo = TaskRepository(db_session)

    user = User(name="singleuser", email="s@s.com", password="p", role="user")
    db_session.add(user)
    await db_session.flush()

    new_task = Task(
        name="Specific Task", user_id=user.user_id, task_type=TaskType.REMINDER
    )
    db_session.add(new_task)
    await db_session.flush()

    found_task = await repo.get_task_id_db(new_task.task_id)

    assert found_task is not None
    assert found_task.task_id == new_task.task_id
    assert found_task.name == "Specific Task"


@pytest.mark.asyncio
async def test_delete_task_db_cascades_to_periodic_task(db_session):
    repo = TaskRepository(db_session)

    user = User(name="deluser", email="d@d.com", password="p", role="user")
    db_session.add(user)
    await db_session.flush()

    task = Task(name="DeleteMe", user_id=user.user_id, task_type=TaskType.REMINDER)
    db_session.add(task)
    await db_session.flush()

    periodic_task = PeriodicTask(
        name=f"User-{user.user_id}-Task-{task.task_id}",
        task="reminder",
        enabled=True,
        discriminator="clockedschedule",
        schedule_id=1,
    )
    db_session.add(periodic_task)
    await db_session.flush()

    await repo.delete_task_db(task.task_id)

    task_check = await db_session.execute(
        select(Task).where(Task.task_id == task.task_id)
    )
    assert task_check.scalar_one_or_none() is None

    periodic_check = await db_session.execute(
        select(PeriodicTask).where(PeriodicTask.name == periodic_task.name)
    )
    assert periodic_check.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_delete_task_db_non_existent(db_session):
    repo = TaskRepository(db_session)

    await repo.delete_task_db(9999)
    assert True

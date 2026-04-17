import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta

from app.services.schedule import create_dynamic_task
from app.services.send_reminder_service import send_reminder
from app.services.send_comic_service import send_comic
from app.services.system_check_service import system_check
from app.schemas.task_schema import TaskCreate, TaskType, TaskStatus
from sqlalchemy import select
from app.models.user_model import User
from app.models.task_model import Task
from sqlalchemy_celery_beat.models import (
    PeriodicTask,
)


@pytest.mark.asyncio
async def test_create_dynamic_task_reminder(db_session):
    user = User(name="test", email="t@t.com", password="p", role="user")
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)

    data = TaskCreate(
        name="Morning Reminder",
        task_type=TaskType.REMINDER,
        description="Test desc",
        interval_time=0,
        schedule_time=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    result = await create_dynamic_task(data, user.user_id, db_session)

    assert "Task Morning Reminder scheduled successfully" in result["message"]

    res = await db_session.execute(select(Task).where(Task.user_id == user.user_id))
    task_in_db = res.scalar_one()
    assert task_in_db.name == "Morning Reminder"

    periodic_res = await db_session.execute(
        select(PeriodicTask).where(PeriodicTask.task == "reminder")
    )
    periodic_task = periodic_res.scalar_one()

    assert periodic_task.one_off is True
    assert json.loads(periodic_task.args) == [user.user_id, task_in_db.task_id]


@pytest.mark.asyncio
async def test_send_reminder_logic(db_session):
    user = User(name="test", email="test@test.com", password="pwd", role="user")
    db_session.add(user)
    await db_session.flush()

    task = Task(
        name="Remind Me",
        user_id=user.user_id,
        task_type=TaskType.REMINDER,
        status=TaskStatus.PENDING,
    )
    db_session.add(task)
    await db_session.flush()

    mock_mail_client = AsyncMock()

    with patch("app.utils.mail_utils.mail.create_message", return_value="msg"):
        await send_reminder(user.user_id, task.task_id, db_session, mock_mail_client)

    await db_session.refresh(task)
    assert task.status == TaskStatus.COMPLETED
    assert task.last_run_at is not None
    mock_mail_client.send_message.assert_awaited_once_with("msg")


@pytest.mark.asyncio
async def test_send_reminder_failure(db_session):
    user = User(name="failure_user", email="fail@test.com", password="pwd", role="user")
    db_session.add(user)
    await db_session.flush()

    task = Task(
        name="Failed Reminder",
        user_id=user.user_id,
        task_type=TaskType.REMINDER,
        status=TaskStatus.PENDING,
    )
    db_session.add(task)
    await db_session.flush()

    mock_mail_client = AsyncMock()
    mock_mail_client.send_message.side_effect = Exception("SMTP Connection Timeout")

    with patch("app.utils.mail_utils.mail.create_message", return_value="msg"):
        with pytest.raises(Exception) as excinfo:
            await send_reminder(
                user.user_id, task.task_id, db_session, mock_mail_client
            )

        assert "SMTP Connection Timeout" in str(excinfo.value)

    await db_session.refresh(task)

    assert task.status == TaskStatus.FAILED
    assert task.last_run_at is None

    mock_mail_client.send_message.assert_awaited_once_with("msg")


@pytest.mark.asyncio
async def test_send_comic_success(db_session):
    user = User(name="comic_lover", email="comic@test.com", password="p", role="user")
    db_session.add(user)
    await db_session.flush()

    task = Task(
        name="Weekly Comic",
        user_id=user.user_id,
        task_type=TaskType.SEND_COMIC,
        status=TaskStatus.PENDING,
    )
    db_session.add(task)
    await db_session.flush()

    mock_mail_client = AsyncMock()

    mock_comic_data = {
        "title": "Test Comic",
        "img": "https://xkcd.com",
        "alt": "Test alt text",
    }

    with (
        patch("httpx.AsyncClient.get") as mock_get,
        patch("app.utils.mail_utils.mail.create_message") as mock_create_msg,
    ):

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_comic_data
        mock_get.return_value = mock_response

        mock_create_msg.return_value = "mocked_email_object"

        await send_comic(user.user_id, task.task_id, db_session, mock_mail_client)

    await db_session.refresh(task)

    assert task.status == TaskStatus.COMPLETED
    assert task.last_run_at is not None

    mock_create_msg.assert_called_once()
    mock_mail_client.send_message.assert_awaited_once_with("mocked_email_object")

    mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_send_comic_api_failure(db_session):
    user = User(name="comic", email="c@c.com", password="p", role="user")
    db_session.add(user)
    await db_session.flush()

    task = Task(
        name="Comic",
        user_id=user.user_id,
        task_type=TaskType.SEND_COMIC,
        status=TaskStatus.PENDING,
    )
    db_session.add(task)
    await db_session.flush()

    mock_mail = AsyncMock()

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=500)
        mock_get.return_value.raise_for_status.side_effect = Exception("API Down")

        with pytest.raises(Exception):
            await send_comic(user.user_id, task.task_id, db_session, mock_mail)

        await db_session.refresh(task)
        assert task.status == TaskStatus.FAILED


@pytest.mark.asyncio
async def test_system_check_success(db_session):
    user = User(name="sys_admin", email="admin@test.com", password="pwd", role="user")
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)

    task = Task(
        name="SysCheck",
        user_id=user.user_id,
        task_type=TaskType.SYSTEM_CHECK,
        status=TaskStatus.PENDING,
    )
    db_session.add(task)
    await db_session.flush()

    with patch("shutil.disk_usage") as mock_disk:
        mock_disk.return_value = MagicMock(total=100 * 1024**3, used=50 * 1024**3)

        await system_check(user.user_id, task.task_id, db_session)

    await db_session.refresh(task)
    assert task.status == TaskStatus.COMPLETED
    assert "used: 50.0 GB" in task.description
    assert "total: 100.0 GB" in task.description


@pytest.mark.asyncio
async def test_system_check_failure(db_session):
    user = User(name="sys_fail", email="fail@system.com", password="pwd", role="user")
    db_session.add(user)
    await db_session.flush()

    task = Task(
        name="SysCheck Fail",
        user_id=user.user_id,
        task_type=TaskType.SYSTEM_CHECK,
        status=TaskStatus.PENDING,
    )
    db_session.add(task)
    await db_session.flush()

    with patch("shutil.disk_usage") as mock_disk:
        mock_disk.side_effect = OSError("Drive not found")

        with pytest.raises(OSError) as excinfo:
            await system_check(user.user_id, task.task_id, db_session)

        assert "Drive not found" in str(excinfo.value)

    await db_session.refresh(task)

    assert task.status == TaskStatus.PENDING
    assert task.last_run_at is None

    assert "used:" not in (task.description or "")

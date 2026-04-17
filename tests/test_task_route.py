import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_create_task_route(authenticated_client):
    payload = {
        "name": "Morning Sync",
        "description": "Daily standup task",
        "task_type": "reminder",
        "interval_time": 0,
        "schedule_time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    with patch(
        "app.api.task.create_dynamic_task", new_callable=AsyncMock
    ) as mock_service:
        mock_service.return_value = {
            "message": "Task Morning Sync scheduled successfully"
        }

        response = await authenticated_client.post("/tasks/", json=payload)

        assert response.status_code == 200
        assert response.json()["message"] == "Task Morning Sync scheduled successfully"
        mock_service.assert_called_once()


@pytest.mark.asyncio
async def test_get_all_tasks_route(authenticated_client):
    mock_data = [{"task_id": 1, "title": "Test Task"}]

    with patch(
        "app.api.task.TaskService.get_tasks", new_callable=AsyncMock
    ) as mock_method:
        mock_method.return_value = mock_data

        response = await authenticated_client.get("/tasks/")

        assert response.status_code == 200
        assert len(response.json()) == 1
        mock_method.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_task_by_route(authenticated_client):
    mock_data = [{"task_id": 1, "title": "Test Task"}]

    with patch(
        "app.api.task.TaskService.get_tasks", new_callable=AsyncMock
    ) as mock_method:
        mock_method.return_value = mock_data

        response = await authenticated_client.get("/tasks/")

        assert response.status_code == 200
        assert len(response.json()) == 1
        mock_method.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_delete_task_route(authenticated_client):
    task_id = 99

    with patch(
        "app.api.task.TaskService.delete_task_id", new_callable=AsyncMock
    ) as mock_del:
        mock_del.return_value = {"message": "deleted"}

        response = await authenticated_client.delete(f"/tasks/{task_id}")

        assert response.status_code == 200
        mock_del.assert_called_once_with(task_id)


@pytest.mark.asyncio
async def test_trigger_task_route(authenticated_client):
    task_id = 5

    with patch(
        "app.api.task.TaskService.trigger", new_callable=AsyncMock
    ) as mock_trigger:
        mock_trigger.return_value = {"status": "triggered"}

        response = await authenticated_client.post(f"/tasks/trigger/{task_id}")

        assert response.status_code == 200
        mock_trigger.assert_called_once_with(task_id)

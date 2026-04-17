import pytest
from unittest.mock import patch, AsyncMock
from app.schemas.user_schema import RegisterResponse


@pytest.mark.asyncio
async def test_register_success(client):
    payload = {
        "name": "testuser",
        "email": "test@example.com",
        "password": "securepassword123",
    }

    mock_return = {
        "email": "test@example.com",
    }

    with patch(
        "app.api.auth.AuthService.register", new_callable=AsyncMock
    ) as mock_register:
        mock_register.return_value = mock_return

        response = await client.post("/auth/register", json=payload)

        assert response.status_code == 200
        assert response.json()["email"] == "test@example.com"
        mock_register.assert_called_once()


@pytest.mark.asyncio
async def test_login_success(client):
    form_data = {"username": "testuser@example.com", "password": "password123"}

    mock_return = {"access_token": "fake_access_token", "token_type": "bearer"}

    with patch("app.api.auth.AuthService.login", new_callable=AsyncMock) as mock_login:
        mock_login.return_value = mock_return

        response = await client.post("/auth/login", data=form_data)

        assert response.status_code == 200
        assert response.json()["access_token"] == "fake_access_token"
        mock_login.assert_called_once()


@pytest.mark.asyncio
async def test_refresh_token_success(client):
    payload = {"refresh_token": "valid_refresh_token"}

    mock_return = {
        "access_token": "new_access_token",
        "refresh_token": "new_refresh_token",
        "token_type": "bearer",
    }

    with patch(
        "app.api.auth.AuthService.refresh_token", new_callable=AsyncMock
    ) as mock_refresh:
        mock_refresh.return_value = mock_return

        response = await client.post("/auth/refresh", json=payload)

        assert response.status_code == 200
        assert response.json()["access_token"] == "new_access_token"
        mock_refresh.assert_called_once()


@pytest.mark.asyncio
async def test_logout_success(client):
    cookies = {"refresh_token": "some_token"}

    mock_return = {"message": "Logged out successfully"}

    with patch(
        "app.api.auth.AuthService.logout", new_callable=AsyncMock
    ) as mock_logout:
        mock_logout.return_value = mock_return

        response = await client.post("/auth/logout", cookies=cookies)

        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"
        mock_logout.assert_called_once()

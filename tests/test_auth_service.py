import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from app.services.auth_service import AuthService
from app.error.custom_execption import (
    UserAlreadyExists,
    InvalidToken,
)


@pytest.mark.asyncio
async def test_register_service_success():
    mock_db = MagicMock()
    mock_ctx = AsyncMock()
    mock_db.begin.return_value = mock_ctx

    mock_payload = MagicMock()
    mock_payload.email = "new@test.com"
    mock_payload.password = "plain_password"
    mock_payload.model_dump.return_value = {
        "email": "new@test.com",
        "password": "hashed_password",
    }

    with (
        patch("app.services.auth_service.UserRepository") as MockRepoClass,
        patch(
            "app.services.auth_service.hash_password", return_value="hashed_password"
        ),
    ):

        mock_repo_instance = MockRepoClass.return_value
        mock_repo_instance.get_by_email = AsyncMock(return_value=None)

        created_user = MagicMock()
        created_user.email = "new@test.com"
        mock_repo_instance.create_user_db = AsyncMock(return_value=created_user)

        service = AuthService(db=mock_db)

        result = await service.register(mock_payload)

        assert result["email"] == "new@test.com"
        mock_repo_instance.create_user_db.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_service_user_exists():
    mock_db = MagicMock()
    mock_ctx = AsyncMock()
    mock_db.begin.return_value = mock_ctx

    mock_payload = MagicMock(email="exists@test.com", password="password")

    with patch("app.services.auth_service.UserRepository") as MockRepo:
        mock_repo_instance = MockRepo.return_value
        mock_repo_instance.get_by_email = AsyncMock(return_value={"id": 1})

        service = AuthService(db=mock_db)

        with pytest.raises(UserAlreadyExists):
            await service.register(mock_payload)


@pytest.mark.asyncio
async def test_login_service_success():
    mock_db = MagicMock()
    mock_ctx = AsyncMock()
    mock_db.begin.return_value = mock_ctx

    mock_response = MagicMock()
    mock_payload = MagicMock(username="test@test.com", password="correct_password")
    mock_user = MagicMock(user_id=1, role="user", password="hashed_password")

    with (
        patch("app.services.auth_service.UserRepository") as MockRepo,
        patch("app.services.auth_service.verify_password", return_value=True),
        patch(
            "app.services.auth_service.create_access_token", return_value="access_token"
        ),
        patch(
            "app.services.auth_service.create_refresh_token",
            return_value="refresh_token",
        ),
    ):

        mock_repo_instance = MockRepo.return_value
        mock_repo_instance.get_by_email = AsyncMock(return_value=mock_user)
        mock_repo_instance.store_refresh_token = AsyncMock()

        service = AuthService(db=mock_db)

        result = await service.login(mock_payload, mock_response)

        assert result.access_token == "access_token"
        assert result.refresh_token == "refresh_token"

        mock_response.set_cookie.assert_called_once()

        mock_repo_instance.store_refresh_token.assert_awaited_once_with(
            1, "refresh_token"
        )


@pytest.mark.asyncio
async def test_refresh_token_reuse_detection():
    mock_db = MagicMock()
    mock_db.begin.return_value = AsyncMock()

    mock_payload = MagicMock(refresh_token="stolen_token")
    mock_db_token = MagicMock(is_used=True, user_id=1)

    with patch("app.services.auth_service.UserRepository") as MockRepo:
        mock_repo_instance = MockRepo.return_value
        mock_repo_instance.get_refresh_token = AsyncMock(return_value=mock_db_token)
        mock_repo_instance.security_check = AsyncMock()

        service = AuthService(db=mock_db)

        with pytest.raises(HTTPException) as exc:
            await service.refresh_token(mock_payload)

        assert exc.value.status_code == 403
        mock_repo_instance.security_check.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_refresh_token_expired():
    # 1. Setup Mock DB
    mock_db = MagicMock()
    mock_db.begin.return_value = AsyncMock()

    mock_payload = MagicMock(refresh_token="expired_token")
    past_time = datetime.now(timezone.utc) - timedelta(days=1)
    mock_db_token = MagicMock(
        expires_at=past_time, refresh_token="expired_token", is_used=False
    )

    with patch("app.services.auth_service.UserRepository") as MockRepo:
        mock_repo_instance = MockRepo.return_value
        mock_repo_instance.get_refresh_token = AsyncMock(return_value=mock_db_token)
        mock_repo_instance.delete_refresh_token = AsyncMock()

        service = AuthService(db=mock_db)

        with pytest.raises(InvalidToken):
            await service.refresh_token(mock_payload)

        mock_repo_instance.delete_refresh_token.assert_awaited_once_with(
            "expired_token"
        )


@pytest.mark.asyncio
async def test_logout_service_success():
    mock_db = MagicMock()
    mock_db.begin.return_value = AsyncMock()

    mock_response = MagicMock()
    refresh_token = "valid_token"

    with patch("app.services.auth_service.UserRepository") as MockRepo:
        mock_repo_instance = MockRepo.return_value
        mock_repo_instance.delete_refresh_token = AsyncMock()

        service = AuthService(db=mock_db)
        result = await service.logout(mock_response, refresh_token)

        assert "logged out" in result["message"].lower()
        mock_repo_instance.delete_refresh_token.assert_awaited_once_with(refresh_token)

        mock_response.delete_cookie.assert_called_once_with(
            key="refresh_token", httponly=True, secure=True, samesite="lax"
        )

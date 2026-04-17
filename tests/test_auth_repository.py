import pytest
from datetime import datetime, timezone
from app.repositories.user_repository import UserRepository
from app.models.user_model import User
from app.models.refresh_token_model import RefreshToken


@pytest.mark.asyncio
async def test_create_user_db_success(db_session):
    repo = UserRepository(db_session)

    user_data = {
        "name": "testrepo",
        "email": "repo@test.com",
        "password": "hashed_password",
    }

    new_user = await repo.create_user_db(user_data)

    assert new_user.user_id is not None
    assert new_user.role == "user"

    user_in_db = await db_session.get(User, new_user.user_id)
    assert user_in_db is not None
    assert user_in_db.email == "repo@test.com"


@pytest.mark.asyncio
async def test_get_by_email_success(db_session):
    repo = UserRepository(db_session)

    test_user = User(name="findme", email="find@test.com", password="pwd", role="user")
    db_session.add(test_user)
    await db_session.flush()

    found_user = await repo.get_by_email("find@test.com")

    assert found_user is not None
    assert found_user.name == "findme"
    assert found_user.email == "find@test.com"


@pytest.mark.asyncio
async def test_store_and_get_refresh_token(db_session):
    repo = UserRepository(db_session)

    user = User(name="tokenuser", email="t@t.com", password="p", role="user")
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)

    token_str = "secret_refresh_token_123"

    await repo.store_refresh_token(user.user_id, token_str)

    db_token = await repo.get_refresh_token(token_str)

    assert db_token is not None
    assert db_token.refresh_token == token_str
    assert db_token.user_id == user.user_id
    assert db_token.is_used is False


@pytest.mark.asyncio
async def test_security_check_deletes_all_user_tokens(db_session):
    repo = UserRepository(db_session)

    user = User(name="security", email="s@s.com", password="p", role="user")
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)

    token1 = RefreshToken(
        refresh_token="t1",
        user_id=user.user_id,
        expires_at=datetime.now(timezone.utc),
        is_used=False,
    )
    token2 = RefreshToken(
        refresh_token="t2",
        user_id=user.user_id,
        expires_at=datetime.now(timezone.utc),
        is_used=False,
    )
    db_session.add_all([token1, token2])
    await db_session.flush()

    await repo.security_check(user.user_id)

    t1 = await repo.get_refresh_token("t1")
    t2 = await repo.get_refresh_token("t2")
    assert t1 is None
    assert t2 is None


@pytest.mark.asyncio
async def test_delete_specific_refresh_token(db_session):
    repo = UserRepository(db_session)

    user = User(name="del", email="del@t.com", password="p", role="user")
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)

    db_token = RefreshToken(
        refresh_token="delete_this_token",
        user_id=user.user_id,
        expires_at=datetime.now(timezone.utc),
        is_used=False,
    )
    db_session.add(db_token)
    await db_session.flush()

    await repo.delete_refresh_token("delete_this_token")

    result = await repo.get_refresh_token("delete_this_token")
    assert result is None

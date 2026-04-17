import pytest
import asyncio
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

from app.main import app
from app.db.base import Base
from sqlalchemy_celery_beat.models import ModelBase as BeatBase
from app.dependencies.get_session import get_db
from app.core.config import settings
from app.middleware.log_middleware import RequestLoggingMiddleware
from app.schemas.token_schema import TokenData
from app.dependencies.current_user import get_current_user

TEST_DATABASE_URL = settings.TEST_DB_URL

from sqlalchemy.pool import NullPool


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


engine_test = create_async_engine(
    settings.TEST_DB_URL,
    poolclass=NullPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine_test, expire_on_commit=False, class_=AsyncSession
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    async with engine_test.begin() as conn:

        await conn.run_sync(Base.metadata.create_all)

        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS celery_schema"))
        await conn.run_sync(BeatBase.metadata.create_all)

    yield

    async with engine_test.begin() as conn:
        await conn.run_sync(BeatBase.metadata.drop_all)
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    async with engine_test.connect() as connection:
        await connection.begin()
        async with TestingSessionLocal(bind=connection) as session:
            yield session
            await session.rollback()


@pytest_asyncio.fixture(autouse=True)
def override_middleware():

    original_middleware = app.user_middleware.copy()
    app.user_middleware = [
        m for m in app.user_middleware if m.cls != RequestLoggingMiddleware
    ]
    app.middleware_stack = app.build_middleware_stack()

    yield

    app.user_middleware = original_middleware
    app.middleware_stack = app.build_middleware_stack()


@pytest_asyncio.fixture
async def client(db_session):
    """
    FastAPI AsyncClient fixture that overrides get_db
    to use the test database session.
    """

    def _get_db_override():
        yield db_session

    app.dependency_overrides[get_db] = _get_db_override

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://127.0.0.1:8000"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def authenticated_client(client):
    mock_user = TokenData(user_id=1, role="user")

    app.dependency_overrides[get_current_user] = lambda: mock_user

    yield client

    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]

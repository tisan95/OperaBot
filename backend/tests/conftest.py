"""Pytest configuration and fixtures."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.db.database import Base, get_db
from app.main import app
from httpx import AsyncClient


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_db():
    """Create test database session.

    Yields:
        AsyncSession instance
    """
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
def override_get_db(test_db):
    """Override get_db dependency for testing.

    Args:
        test_db: Test database session

    Returns:
        Function to override dependency
    """
    async def get_test_db():
        yield test_db

    return get_test_db


@pytest_asyncio.fixture
async def async_client(override_get_db):
    """Create async test client.

    Args:
        override_get_db: Override function

    Yields:
        AsyncClient instance
    """
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()

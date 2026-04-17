"""Unit tests for authentication service."""

import pytest_asyncio
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.db.database import Base
from app.services.auth_service import AuthService
from app.utils.security import verify_password


@pytest_asyncio.fixture
async def auth_db():
    """Create test database for auth tests.

    Yields:
        AsyncSession instance
    """
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.mark.asyncio
async def test_register_success(auth_db):
    """Test successful user registration."""
    auth_service = AuthService(auth_db)

    result = await auth_service.register(
        email="user@example.com",
        password="SecurePass123!",
        company_name="Test Company",
    )

    assert result["user"]["email"] == "user@example.com"
    assert result["user"]["role"] == "admin"  # First user is admin
    assert "access_token" in result
    assert "refresh_token" in result
    assert result["company"]["name"] == "Test Company"


@pytest.mark.asyncio
async def test_register_invalid_email(auth_db):
    """Test registration with invalid email."""
    auth_service = AuthService(auth_db)

    with pytest.raises(ValueError, match="Invalid email format"):
        await auth_service.register(
            email="invalid-email",
            password="SecurePass123!",
            company_name="Test Company",
        )


@pytest.mark.asyncio
async def test_register_short_password(auth_db):
    """Test registration with short password."""
    auth_service = AuthService(auth_db)

    with pytest.raises(ValueError, match="Password must be at least 8 characters"):
        await auth_service.register(
            email="user@example.com",
            password="short",
            company_name="Test Company",
        )


@pytest.mark.asyncio
async def test_register_duplicate_email(auth_db):
    """Test registration with duplicate email in same company."""
    auth_service = AuthService(auth_db)

    # Register first user
    await auth_service.register(
        email="user@example.com",
        password="SecurePass123!",
        company_name="Test Company",
    )

    # Try to register with same email
    with pytest.raises(ValueError, match="Email already registered"):
        await auth_service.register(
            email="user@example.com",
            password="SecurePass123!",
            company_name="Test Company",
        )


@pytest.mark.asyncio
async def test_login_success(auth_db):
    """Test successful login."""
    auth_service = AuthService(auth_db)

    # Register user first
    await auth_service.register(
        email="user@example.com",
        password="SecurePass123!",
        company_name="Test Company",
    )

    # Login
    result = await auth_service.login(
        email="user@example.com",
        password="SecurePass123!",
        company_name="Test Company",
    )

    assert result["user"]["email"] == "user@example.com"
    assert "access_token" in result
    assert "refresh_token" in result


@pytest.mark.asyncio
async def test_login_invalid_password(auth_db):
    """Test login with invalid password."""
    auth_service = AuthService(auth_db)

    # Register user first
    await auth_service.register(
        email="user@example.com",
        password="SecurePass123!",
        company_name="Test Company",
    )

    # Try to login with wrong password
    with pytest.raises(ValueError, match="Invalid email or password"):
        await auth_service.login(
            email="user@example.com",
            password="WrongPassword",
            company_name="Test Company",
        )


@pytest.mark.asyncio
async def test_first_user_is_admin(auth_db):
    """Test that first user is assigned admin role."""
    auth_service = AuthService(auth_db)

    result1 = await auth_service.register(
        email="admin@example.com",
        password="SecurePass123!",
        company_name="Test Company",
    )

    result2 = await auth_service.register(
        email="user@example.com",
        password="SecurePass123!",
        company_name="Test Company",
    )

    assert result1["user"]["role"] == "admin"
    assert result2["user"]["role"] == "user"

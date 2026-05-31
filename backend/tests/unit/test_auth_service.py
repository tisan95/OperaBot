"""Unit tests for AuthService (SQLite in-memory, no HTTP layer)."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.db.database import Base
from app.services.auth_service import AuthService


@pytest_asyncio.fixture
async def db():
    """Fresh in-memory SQLite DB per test."""
    # Import ALL models so SQLAlchemy can resolve relationships before create_all
    import app.models.company
    import app.models.user
    import app.models.faq
    import app.models.chat_message
    import app.models.document
    import app.models.ticket

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


# ── Registration ──────────────────────────────────────────────────────────────

async def test_first_user_is_super_admin(db):
    svc = AuthService(db)
    result = await svc.register("admin@co.com", "Admin1234!", "TestCo")
    assert result["user"]["role"] == "super_admin"
    assert result["user"]["status"] == "active"
    assert "access_token" in result
    assert result["company"]["name"] == "TestCo"


async def test_second_user_is_pending(db):
    svc = AuthService(db)
    await svc.register("admin@co.com", "Admin1234!", "TestCo")
    result = await svc.register("user@co.com", "User1234!", "TestCo")
    assert result["user"]["role"] == "user"
    assert result["user"]["status"] == "pending"


async def test_register_invalid_email_raises(db):
    svc = AuthService(db)
    with pytest.raises(ValueError, match="Invalid email format"):
        await svc.register("not-an-email", "Admin1234!", "TestCo")


async def test_register_short_password_raises(db):
    svc = AuthService(db)
    with pytest.raises(ValueError, match="Password must be at least 8 characters"):
        await svc.register("admin@co.com", "short", "TestCo")


async def test_register_duplicate_email_raises(db):
    svc = AuthService(db)
    await svc.register("admin@co.com", "Admin1234!", "TestCo")
    with pytest.raises(ValueError, match="Email already registered"):
        await svc.register("admin@co.com", "Admin1234!", "TestCo")


# ── Login ─────────────────────────────────────────────────────────────────────

async def test_login_success(db):
    svc = AuthService(db)
    await svc.register("admin@co.com", "Admin1234!", "TestCo")
    result = await svc.login("admin@co.com", "Admin1234!", "TestCo")
    assert result["user"]["email"] == "admin@co.com"
    assert "access_token" in result


async def test_login_wrong_password_raises(db):
    svc = AuthService(db)
    await svc.register("admin@co.com", "Admin1234!", "TestCo")
    with pytest.raises(ValueError, match="Invalid email or password"):
        await svc.login("admin@co.com", "WrongPass!", "TestCo")


async def test_login_company_not_found_raises(db):
    svc = AuthService(db)
    with pytest.raises(ValueError, match="Company not found"):
        await svc.login("admin@co.com", "Admin1234!", "NoSuchCo")


async def test_login_multi_tenant_isolation(db):
    """Same email in different companies are independent."""
    svc = AuthService(db)
    await svc.register("admin@co.com", "Admin1234!", "Co-A")
    with pytest.raises(ValueError):
        await svc.login("admin@co.com", "Admin1234!", "Co-B")

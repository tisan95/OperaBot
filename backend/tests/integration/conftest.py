"""Shared fixtures for integration tests.

Each test gets:
- A fresh ASGI client (function scope)
- An auto-use DB cleanup after every test (delete all rows)
- admin_auth / user_auth / admin_session convenience fixtures

Note: httpx ASGITransport does NOT trigger the FastAPI lifespan, so tables must
be created explicitly via the setup_tables fixture before requests are made.
"""

import asyncio
import os
import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete

BASE = "http://test"


# ── One-time table creation (synchronous, session scope) ─────────────────────

@pytest.fixture(scope="session", autouse=True)
def setup_tables():
    """Create SQLite schema once per test session (before any async fixture)."""
    # Import all models so Base.metadata knows every table
    import app.models.company         # noqa: F401
    import app.models.user            # noqa: F401
    import app.models.faq             # noqa: F401
    import app.models.chat_session    # noqa: F401  ← must come before chat_message
    import app.models.chat_message    # noqa: F401
    import app.models.document        # noqa: F401
    import app.models.ticket          # noqa: F401

    from app.db.database import engine, Base

    async def _create():
        async with engine.begin() as conn:
            # Always rebuild the schema so new columns/tables are picked up.
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    loop = asyncio.new_event_loop()
    loop.run_until_complete(_create())
    loop.close()
    yield


# ── ASGI client ───────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def client(setup_tables):
    """Per-test ASGI client."""
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE) as c:
        yield c


# ── DB cleanup after each test ────────────────────────────────────────────────

@pytest_asyncio.fixture(autouse=True)
async def clean_db():
    """Delete all rows from every table after each test for isolation."""
    yield
    from app.db.database import AsyncSessionLocal
    from app.models.ticket import Ticket, TicketNote
    from app.models.chat_message import ChatMessage
    from app.models.chat_session import ChatSession
    from app.models.document import Document
    from app.models.faq import FAQ
    from app.models.user import User
    from app.models.company import Company

    async with AsyncSessionLocal() as session:
        for model in [TicketNote, Ticket, Document, ChatMessage, ChatSession, FAQ, User, Company]:
            try:
                await session.execute(delete(model))
            except Exception:
                pass
        try:
            await session.commit()
        except Exception:
            await session.rollback()


# ── Email stub — never hit a real SMTP/HTTP endpoint during tests ────────────

@pytest_asyncio.fixture(autouse=True)
async def _stub_email(monkeypatch):
    """Email is best-effort and network-bound; tests must not depend on a
    running MailHog. Individual tests can still monkeypatch the route-level
    send_welcome_email/send_ticket_resolved_email imports to assert calls."""
    async def _noop_send(*args, **kwargs):
        return True
    monkeypatch.setattr("app.services.email_service.send_email", _noop_send)


# ── Auth helpers ──────────────────────────────────────────────────────────────

def _uniq() -> str:
    return uuid.uuid4().hex[:8]


@pytest_asyncio.fixture
async def admin_auth(client):
    """Register a fresh company + super_admin. Returns cookies and response data."""
    u = _uniq()
    r = await client.post("/auth/register", json={
        "email": f"admin-{u}@test.com",
        "password": "Admin1234!",
        "company_name": f"Co-{u}",
    })
    assert r.status_code == 201, f"Admin register failed: {r.text}"
    return {"cookies": dict(r.cookies), "data": r.json()}


@pytest_asyncio.fixture
async def user_auth(client, admin_auth):
    """Register + activate a regular user in the admin's company."""
    u = _uniq()
    company = admin_auth["data"]["company"]["name"]
    email = f"user-{u}@test.com"

    r = await client.post("/auth/register", json={
        "email": email, "password": "User1234!", "company_name": company,
    })
    assert r.status_code == 201, f"User register failed: {r.text}"
    user_id = r.json()["user"]["id"]

    r2 = await client.patch(
        f"/users/{user_id}/approve",
        json={"role": "user"},
        cookies=admin_auth["cookies"],
    )
    assert r2.status_code == 200, f"User approve failed: {r2.text}"

    r3 = await client.post("/auth/login", json={
        "email": email, "password": "User1234!", "company_name": company,
    })
    assert r3.status_code == 200, f"User login failed: {r3.text}"
    return {"cookies": dict(r3.cookies), "data": r3.json()}


@pytest_asyncio.fixture
async def admin_session(client, admin_auth):
    """Create a chat session for the admin user and return its id."""
    r = await client.post("/chat/sessions", cookies=admin_auth["cookies"])
    assert r.status_code == 201, f"Session create failed: {r.text}"
    return r.json()["id"]

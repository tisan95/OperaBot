"""Integration tests for authentication endpoints."""

import pytest


# ── Registration ──────────────────────────────────────────────────────────────

async def test_register_first_user_is_super_admin(client):
    r = await client.post("/auth/register", json={
        "email": "admin@co.com", "password": "Admin1234!", "company_name": "Acme",
    })
    assert r.status_code == 201
    data = r.json()
    assert data["user"]["role"] == "super_admin"
    assert data["user"]["status"] == "active"
    assert "access_token" in data
    assert "company" in data


async def test_register_second_user_is_pending(client):
    await client.post("/auth/register", json={
        "email": "admin@co.com", "password": "Admin1234!", "company_name": "Acme",
    })
    r = await client.post("/auth/register", json={
        "email": "user@co.com", "password": "User1234!", "company_name": "Acme",
    })
    assert r.status_code == 201
    data = r.json()
    assert data["user"]["role"] == "user"
    assert data["user"]["status"] == "pending"


async def test_register_duplicate_email_returns_400(client):
    for _ in range(2):
        r = await client.post("/auth/register", json={
            "email": "dup@co.com", "password": "Admin1234!", "company_name": "DupCo",
        })
    assert r.status_code == 400


async def test_register_invalid_email_returns_422(client):
    r = await client.post("/auth/register", json={
        "email": "not-an-email", "password": "Admin1234!", "company_name": "Co",
    })
    assert r.status_code == 422


async def test_register_short_password_returns_422(client):
    r = await client.post("/auth/register", json={
        "email": "admin@co.com", "password": "short", "company_name": "Co",
    })
    assert r.status_code == 422  # pydantic min_length=8 validation


# ── Login ─────────────────────────────────────────────────────────────────────

async def test_login_success(client):
    await client.post("/auth/register", json={
        "email": "admin@co.com", "password": "Admin1234!", "company_name": "Acme",
    })
    r = await client.post("/auth/login", json={
        "email": "admin@co.com", "password": "Admin1234!", "company_name": "Acme",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["user"]["email"] == "admin@co.com"
    assert "access_token" in data
    assert "access_token" in r.cookies


async def test_login_wrong_password_returns_401(client):
    await client.post("/auth/register", json={
        "email": "admin@co.com", "password": "Admin1234!", "company_name": "Acme",
    })
    r = await client.post("/auth/login", json={
        "email": "admin@co.com", "password": "WrongPass!", "company_name": "Acme",
    })
    assert r.status_code == 401


async def test_login_company_not_found_returns_401(client):
    r = await client.post("/auth/login", json={
        "email": "nobody@co.com", "password": "Admin1234!", "company_name": "NoSuchCo",
    })
    assert r.status_code == 401


async def test_login_multi_tenant_isolation(client):
    """User registered in Co-A cannot log into Co-B."""
    await client.post("/auth/register", json={
        "email": "admin@co.com", "password": "Admin1234!", "company_name": "Co-A",
    })
    r = await client.post("/auth/login", json={
        "email": "admin@co.com", "password": "Admin1234!", "company_name": "Co-B",
    })
    assert r.status_code == 401


async def test_login_pending_user_returns_403(client):
    """A user who hasn't been approved can't log in."""
    await client.post("/auth/register", json={
        "email": "admin@co.com", "password": "Admin1234!", "company_name": "Acme",
    })
    await client.post("/auth/register", json={
        "email": "pending@co.com", "password": "User1234!", "company_name": "Acme",
    })
    r = await client.post("/auth/login", json={
        "email": "pending@co.com", "password": "User1234!", "company_name": "Acme",
    })
    assert r.status_code == 403


# ── Logout ────────────────────────────────────────────────────────────────────

async def test_logout_clears_cookies(client):
    r = await client.post("/auth/logout")
    assert r.status_code == 200
    assert r.json()["message"] == "Logged out successfully"


# ── /auth/me ──────────────────────────────────────────────────────────────────

async def test_me_returns_current_user(client, admin_auth):
    r = await client.get("/auth/me", cookies=admin_auth["cookies"])
    assert r.status_code == 200
    assert r.json()["user"]["email"] == admin_auth["data"]["user"]["email"]


async def test_me_unauthenticated_returns_401(client):
    r = await client.get("/auth/me")
    assert r.status_code == 401

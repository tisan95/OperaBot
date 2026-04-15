"""Integration tests for authentication endpoints."""

import pytest


@pytest.mark.asyncio
async def test_register_endpoint(async_client):
    """Test POST /auth/register endpoint."""
    response = await async_client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "company_name": "New Company",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["role"] == "admin"
    assert data["company"]["name"] == "New Company"
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_register_invalid_email(async_client):
    """Test registration with invalid email."""
    response = await async_client.post(
        "/auth/register",
        json={
            "email": "invalid-email",
            "password": "SecurePass123!",
            "company_name": "Test Company",
        },
    )

    assert response.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_login_endpoint(async_client):
    """Test POST /auth/login endpoint."""
    # Register first
    await async_client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "password": "SecurePass123!",
            "company_name": "Test Company",
        },
    )

    # Login
    response = await async_client.post(
        "/auth/login",
        json={
            "email": "user@example.com",
            "password": "SecurePass123!",
            "company_name": "Test Company",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "user@example.com"
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client):
    """Test login with invalid credentials."""
    # Register first
    await async_client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "password": "SecurePass123!",
            "company_name": "Test Company",
        },
    )

    # Try to login with wrong password
    response = await async_client.post(
        "/auth/login",
        json={
            "email": "user@example.com",
            "password": "WrongPassword",
            "company_name": "Test Company",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_endpoint(async_client):
    """Test POST /auth/logout endpoint."""
    response = await async_client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"


@pytest.mark.asyncio
async def test_health_check(async_client):
    """Test health check endpoint."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_multi_tenant_isolation(async_client):
    """Test that users from different companies are isolated."""
    # Register user in company A
    await async_client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "password": "SecurePass123!",
            "company_name": "Company A",
        },
    )

    # Try to login to company B with same email (should fail)
    response = await async_client.post(
        "/auth/login",
        json={
            "email": "user@example.com",
            "password": "SecurePass123!",
            "company_name": "Company B",
        },
    )

    assert response.status_code == 401
    assert "Company not found" in response.json()["detail"]

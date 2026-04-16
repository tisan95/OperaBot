"""Integration tests for FAQ endpoints."""

import pytest


@pytest.mark.asyncio
async def test_faq_endpoints_create_and_list(async_client):
    """Test that authenticated users can create and list FAQs."""
    # Register a user
    register_response = await async_client.post(
        "/auth/register",
        json={
            "email": "faquser@example.com",
            "password": "SecurePass123!",
            "company_name": "FAQ Company",
        },
    )

    assert register_response.status_code == 201
    assert "access_token" in register_response.json()

    # Login to establish cookies for authenticated requests
    login_response = await async_client.post(
        "/auth/login",
        json={
            "email": "faquser@example.com",
            "password": "SecurePass123!",
            "company_name": "FAQ Company",
        },
    )
    assert login_response.status_code == 200

    # Create a new FAQ entry
    create_response = await async_client.post(
        "/faqs",
        json={
            "question": "What is OperaBot?",
            "answer": "OperaBot is an operational knowledge assistant.",
            "category": "General",
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["question"] == "What is OperaBot?"
    assert created["answer"] == "OperaBot is an operational knowledge assistant."
    assert created["category"] == "General"
    assert "id" in created
    assert "created_at" in created

    # Fetch FAQs and verify the new entry is present
    list_response = await async_client.get("/faqs")
    assert list_response.status_code == 200
    data = list_response.json()
    assert isinstance(data, list)
    assert any(item["question"] == "What is OperaBot?" for item in data)

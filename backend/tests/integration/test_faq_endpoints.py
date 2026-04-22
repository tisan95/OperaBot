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


@pytest.mark.asyncio
async def test_faq_endpoints_update(async_client):
    """Test that authenticated users can update an FAQ."""
    register_response = await async_client.post(
        "/auth/register",
        json={
            "email": "faqedit@example.com",
            "password": "SecurePass123!",
            "company_name": "FAQ Edit Company",
        },
    )

    assert register_response.status_code == 201

    login_response = await async_client.post(
        "/auth/login",
        json={
            "email": "faqedit@example.com",
            "password": "SecurePass123!",
            "company_name": "FAQ Edit Company",
        },
    )
    assert login_response.status_code == 200

    create_response = await async_client.post(
        "/faqs",
        json={
            "question": "What is an FAQ?",
            "answer": "A frequently asked question.",
            "category": "General",
        },
    )
    assert create_response.status_code == 201
    faq_id = create_response.json()["id"]

    update_response = await async_client.put(
        f"/faqs/{faq_id}",
        json={
            "question": "What is an FAQ entry?",
            "answer": "A short question and an answer for users.",
            "category": "Knowledge",
        },
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["id"] == faq_id
    assert updated["question"] == "What is an FAQ entry?"
    assert updated["answer"] == "A short question and an answer for users."
    assert updated["category"] == "Knowledge"

    list_response = await async_client.get("/faqs")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert any(item["question"] == "What is an FAQ entry?" for item in list_data)

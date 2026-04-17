"""Integration tests for chat flows."""

import pytest


@pytest.mark.asyncio
async def test_chat_messages_returns_llm_answer(async_client, monkeypatch):
    async def fake_generate_answer(message, faq_context=None):
        return "Mocked answer from LLM"

    monkeypatch.setattr("app.api.routes.chat.generate_answer", fake_generate_answer)

    register_response = await async_client.post(
        "/auth/register",
        json={
            "email": "chatuser@example.com",
            "password": "SecurePass123!",
            "company_name": "Chat Test Co",
        },
    )
    assert register_response.status_code == 201

    login_response = await async_client.post(
        "/auth/login",
        json={
            "email": "chatuser@example.com",
            "password": "SecurePass123!",
            "company_name": "Chat Test Co",
        },
    )
    assert login_response.status_code == 200

    chat_response = await async_client.post(
        "/chat/messages",
        json={"message": "Hello, what can you do?"},
    )
    assert chat_response.status_code == 201
    payload = chat_response.json()
    assert payload["bot_message"] == "Mocked answer from LLM"
    assert payload["user_message"] == "Hello, what can you do?"


@pytest.mark.asyncio
async def test_chat_history_persistence_and_admin_analytics(async_client, monkeypatch):
    async def fake_generate_answer(message, faq_context=None):
        return "Mocked answer for analytics"

    monkeypatch.setattr("app.api.routes.chat.generate_answer", fake_generate_answer)

    register_response = await async_client.post(
        "/auth/register",
        json={
            "email": "adminchat@example.com",
            "password": "SecurePass123!",
            "company_name": "Analytics Company",
        },
    )
    assert register_response.status_code == 201

    login_response = await async_client.post(
        "/auth/login",
        json={
            "email": "adminchat@example.com",
            "password": "SecurePass123!",
            "company_name": "Analytics Company",
        },
    )
    assert login_response.status_code == 200

    chat_response = await async_client.post(
        "/chat/messages",
        json={"message": "How many FAQs?"},
    )
    assert chat_response.status_code == 201
    payload = chat_response.json()
    assert payload["bot_message"] == "Mocked answer for analytics"
    assert payload["rating"] is None
    assert payload["id"] > 0

    rating_response = await async_client.put(
        f"/chat/messages/{payload['id']}/rating",
        json={"rating": 5},
    )
    assert rating_response.status_code == 200
    rating_payload = rating_response.json()
    assert rating_payload["rating"] == 5

    analytics_response = await async_client.get("/admin/analytics")
    assert analytics_response.status_code == 200
    analytics = analytics_response.json()
    assert analytics["total_chats_today"] == 1
    assert analytics["success_rate"] == 1.0
    assert analytics["top_questions"][0]["question"] == "How many FAQs?"
    assert analytics["top_questions"][0]["count"] == 1

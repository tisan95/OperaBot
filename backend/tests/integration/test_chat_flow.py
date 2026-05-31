"""Integration tests for chat endpoints (greeting / question / escalate)."""

import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────

_RAG_MOCK = {
    "answer": "La respuesta es X.",
    "sources": [],
    "confidence": 0.85,
    "ui_hint": "resolution_prompt",
    "cited_documents": [],
}

_NO_RAG_MOCK = {
    "answer": "No encuentro información sobre esto.",
    "sources": [],
    "confidence": 0.0,
    "ui_hint": "escalate_prompt",
    "cited_documents": [],
}


# ── Intent: instant responses (no LLM / no Qdrant) ───────────────────────────

async def test_greeting_returns_instant_response(client, admin_auth):
    r = await client.post("/chat/messages",
        json={"message": "hola"},
        cookies=admin_auth["cookies"])
    assert r.status_code == 201
    data = r.json()
    assert "OperaBot" in data["bot_message"]
    assert data["confidence"] == 1.0


async def test_greeting_multiword(client, admin_auth):
    r = await client.post("/chat/messages",
        json={"message": "hola buenos días"},
        cookies=admin_auth["cookies"])
    assert r.status_code == 201
    assert r.json()["confidence"] == 1.0


async def test_confirmation_returns_instant_response(client, admin_auth):
    r = await client.post("/chat/messages",
        json={"message": "solucionado"},
        cookies=admin_auth["cookies"])
    assert r.status_code == 201
    assert r.json()["confidence"] == 1.0


async def test_negation_returns_escalate_hint(client, admin_auth):
    r = await client.post("/chat/messages",
        json={"message": "no me funciona"},
        cookies=admin_auth["cookies"])
    assert r.status_code == 201
    data = r.json()
    assert data["ui_hint"] == "escalate_prompt"


# ── Intent: QUESTION with RAG mocked ─────────────────────────────────────────

async def test_question_with_rag_results(client, admin_auth, monkeypatch):
    async def mock_rag(message, company_id, recent_rag_count=0):
        return _RAG_MOCK

    monkeypatch.setattr("app.api.routes.chat.generate_answer_with_sources", mock_rag)

    r = await client.post("/chat/messages",
        json={"message": "¿Cómo hago el proceso de alta?"},
        cookies=admin_auth["cookies"])
    assert r.status_code == 201
    data = r.json()
    assert data["bot_message"] == "La respuesta es X."
    assert data["confidence"] == 0.85
    assert data["ui_hint"] == "resolution_prompt"


async def test_question_without_rag_results(client, admin_auth, monkeypatch):
    async def mock_no_rag(message, company_id, recent_rag_count=0):
        return _NO_RAG_MOCK

    monkeypatch.setattr("app.api.routes.chat.generate_answer_with_sources", mock_no_rag)

    r = await client.post("/chat/messages",
        json={"message": "¿Qué es la termodinámica?"},
        cookies=admin_auth["cookies"])
    assert r.status_code == 201
    data = r.json()
    assert data["ui_hint"] == "escalate_prompt"
    assert data["confidence"] == 0.0


# ── Validation & auth ─────────────────────────────────────────────────────────

async def test_empty_message_returns_400(client, admin_auth):
    r = await client.post("/chat/messages",
        json={"message": "   "},
        cookies=admin_auth["cookies"])
    assert r.status_code == 400


async def test_unauthenticated_returns_401(client):
    r = await client.post("/chat/messages", json={"message": "hola"})
    assert r.status_code == 401


# ── History ───────────────────────────────────────────────────────────────────

async def test_chat_history_returns_messages(client, admin_auth):
    await client.post("/chat/messages",
        json={"message": "hola"},
        cookies=admin_auth["cookies"])
    r = await client.get("/chat/history", cookies=admin_auth["cookies"])
    assert r.status_code == 200
    assert len(r.json()) >= 1


# ── Escalate ──────────────────────────────────────────────────────────────────

async def test_escalate_questions_endpoint(client, admin_auth, monkeypatch):
    async def mock_questions(conversation):
        return {
            "intro": "Para escalar necesito más datos:",
            "questions": ["¿Cuándo ocurre?", "¿Qué error ves?"],
            "context_summary": "Error desconocido",
        }

    monkeypatch.setattr(
        "app.api.routes.chat.generate_escalation_questions", mock_questions
    )
    r = await client.post("/chat/escalate-questions",
        cookies=admin_auth["cookies"])
    assert r.status_code == 200
    data = r.json()
    assert "questions" in data
    assert len(data["questions"]) == 2


async def test_escalate_creates_ticket(client, admin_auth):
    r = await client.post("/chat/escalate",
        json={
            "question": "No puedo acceder al sistema",
            "context_summary": "Error de acceso",
            "answers": ["Ocurre cada mañana", "Sin mensaje de error"],
        },
        cookies=admin_auth["cookies"])
    assert r.status_code == 201
    data = r.json()
    assert "ticket_id" in data
    assert data["ticket_id"] > 0

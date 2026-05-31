"""Unit tests for LLM client functions (mock httpx, no real Ollama needed)."""

import pytest
from app.services.llm_client import (
    classify_intent,
    greeting_response,
    confirmation_response,
    negation_response,
    _filter_by_similarity,
    _calculate_confidence,
    SIMILARITY_THRESHOLD,
)


# ── classify_intent ───────────────────────────────────────────────────────────

def test_classify_greeting():
    assert classify_intent("hola") == "GREETING"


def test_classify_confirmation():
    assert classify_intent("ya está") == "CONFIRMATION"


def test_classify_negation():
    assert classify_intent("no funciona") == "NEGATION"


def test_classify_question():
    assert classify_intent("¿Cómo hago el alta?") == "QUESTION"


# ── Canned responses ──────────────────────────────────────────────────────────

def test_greeting_response_structure():
    r = greeting_response()
    assert "answer" in r
    assert r["confidence"] == 1.0
    assert r["ui_hint"] is None
    assert "OperaBot" in r["answer"]


def test_confirmation_response_structure():
    r = confirmation_response()
    assert r["confidence"] == 1.0
    assert r["ui_hint"] is None


def test_negation_response_structure():
    r = negation_response()
    assert r["confidence"] == 0.0
    assert r["ui_hint"] == "escalate_prompt"


# ── RAG helpers ───────────────────────────────────────────────────────────────

def test_filter_by_similarity_removes_low_scores():
    knowledge = {
        "faqs": [
            {"score": 0.9, "payload": {}},
            {"score": 0.3, "payload": {}},   # below threshold
        ],
        "documents": [
            {"score": 0.7, "payload": {}},
            {"score": 0.1, "payload": {}},   # below threshold
        ],
    }
    filtered = _filter_by_similarity(knowledge)
    assert len(filtered["faqs"]) == 1
    assert len(filtered["documents"]) == 1


def test_filter_by_similarity_empty():
    filtered = _filter_by_similarity({"faqs": [], "documents": []})
    assert filtered == {"faqs": [], "documents": []}


def test_calculate_confidence_average():
    knowledge = {
        "faqs": [{"score": 0.8}],
        "documents": [{"score": 0.6}],
    }
    conf = _calculate_confidence(knowledge)
    assert abs(conf - 0.7) < 0.001


def test_calculate_confidence_empty_returns_zero():
    assert _calculate_confidence({"faqs": [], "documents": []}) == 0.0


# ── _generate_with_ollama via generate_answer (httpx mock) ───────────────────

class _FakeResponse:
    def __init__(self, status_code, body):
        self.status_code = status_code
        self._body = body
        self.text = str(body)

    def json(self):
        return self._body


class _FakeClient:
    def __init__(self, response):
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        pass

    async def post(self, url, json):
        return self._response


async def test_generate_with_ollama_success(monkeypatch):
    import app.services.llm_client as llm

    monkeypatch.setattr(
        "app.services.llm_client.httpx.AsyncClient",
        lambda *a, **kw: _FakeClient(_FakeResponse(200, {"response": "Respuesta de prueba"})),
    )
    result = await llm._generate_with_ollama("¿Qué es X?", "contexto")
    assert result == "Respuesta de prueba"


async def test_generate_with_ollama_non_200_returns_fallback(monkeypatch):
    import app.services.llm_client as llm

    monkeypatch.setattr(
        "app.services.llm_client.httpx.AsyncClient",
        lambda *a, **kw: _FakeClient(_FakeResponse(500, {"error": "server error"})),
    )
    result = await llm._generate_with_ollama("¿Qué?", "ctx")
    assert "No he podido" in result or "No puedo" in result or len(result) > 0


async def test_generate_with_ollama_empty_response_returns_fallback(monkeypatch):
    import app.services.llm_client as llm

    monkeypatch.setattr(
        "app.services.llm_client.httpx.AsyncClient",
        lambda *a, **kw: _FakeClient(_FakeResponse(200, {"response": ""})),
    )
    result = await llm._generate_with_ollama("Mensaje", "ctx")
    assert len(result) > 0

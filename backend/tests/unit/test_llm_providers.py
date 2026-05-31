"""Unit tests for the multi-provider LLM dispatcher (_call_llm)."""

import pytest
import app.services.llm_client as llm
from app.config import settings


class _FakeResp:
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

    async def post(self, url, **kwargs):
        return self._response


def _patch_client(monkeypatch, response):
    monkeypatch.setattr(
        "app.services.llm_client.httpx.AsyncClient",
        lambda *a, **kw: _FakeClient(response),
    )


# ── Ollama ────────────────────────────────────────────────────────────────────

async def test_call_llm_dispatches_to_ollama(monkeypatch):
    settings.LLM_PROVIDER = "ollama"
    _patch_client(monkeypatch, _FakeResp(200, {"response": "Respuesta Ollama"}))
    result = await llm._call_llm("prompt de prueba")
    assert result == "Respuesta Ollama"


async def test_ollama_fallback_on_error(monkeypatch):
    settings.LLM_PROVIDER = "ollama"
    _patch_client(monkeypatch, _FakeResp(500, {"error": "server error"}))
    result = await llm._call_llm("prompt")
    assert len(result) > 0


# ── Groq ─────────────────────────────────────────────────────────────────────

async def test_call_llm_dispatches_to_groq(monkeypatch):
    settings.LLM_PROVIDER = "groq"
    settings.LLM_API_KEY = "fake-groq-key"
    _patch_client(monkeypatch, _FakeResp(200, {
        "choices": [{"message": {"content": "Respuesta Groq"}}]
    }))
    result = await llm._call_llm("prompt de prueba")
    assert result == "Respuesta Groq"


async def test_groq_fallback_on_error(monkeypatch):
    settings.LLM_PROVIDER = "groq"
    settings.LLM_API_KEY = "fake-groq-key"
    _patch_client(monkeypatch, _FakeResp(401, {"error": "invalid api key"}))
    result = await llm._call_llm("prompt")
    assert len(result) > 0


# ── Anthropic ─────────────────────────────────────────────────────────────────

async def test_call_llm_dispatches_to_anthropic(monkeypatch):
    settings.LLM_PROVIDER = "anthropic"
    settings.LLM_API_KEY = "fake-anthropic-key"
    _patch_client(monkeypatch, _FakeResp(200, {
        "content": [{"text": "Respuesta Anthropic"}]
    }))
    result = await llm._call_llm("prompt de prueba")
    assert result == "Respuesta Anthropic"


async def test_anthropic_fallback_on_error(monkeypatch):
    settings.LLM_PROVIDER = "anthropic"
    settings.LLM_API_KEY = "fake-key"
    _patch_client(monkeypatch, _FakeResp(529, {"error": "overloaded"}))
    result = await llm._call_llm("prompt")
    assert len(result) > 0


# ── Unknown provider falls back to Ollama ────────────────────────────────────

async def test_unknown_provider_falls_back_to_ollama(monkeypatch):
    settings.LLM_PROVIDER = "some-unknown-provider"
    _patch_client(monkeypatch, _FakeResp(200, {"response": "Ollama fallback"}))
    result = await llm._call_llm("prompt")
    assert result == "Ollama fallback"

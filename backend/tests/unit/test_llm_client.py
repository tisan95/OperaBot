"""Unit tests for the LLM client."""

import pytest
from app.config import settings
from app.services.llm_client import generate_answer


class FakeResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json_data = json_data
        self.text = str(json_data)
        self.headers = {}  # Add headers attribute required by httpx

    def json(self):
        return self._json_data


class FakeAsyncClient:
    def __init__(self, *args, **kwargs):
        self._response = kwargs.get("response")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, json):
        return self._response


@pytest.mark.asyncio
async def test_generate_answer_ollama_success(monkeypatch):
    settings.LLM_PROVIDER = "ollama"
    settings.LLM_MODEL = "ollama-test"
    settings.LLM_API_KEY = None
    settings.LLM_API_URL = "http://localhost:11434/api/generate"
    settings.LLM_TIMEOUT_SECONDS = 5

    response = FakeResponse(200, {"response": "Hello from Ollama."})

    def fake_async_client(*args, **kwargs):
        return FakeAsyncClient(response=response)

    monkeypatch.setattr("app.services.llm_client.httpx.AsyncClient", fake_async_client)

    answer = await generate_answer("What is OperaBot?", [])
    assert answer == "Hello from Ollama."


@pytest.mark.asyncio
async def test_generate_answer_ollama_fallback_on_malformed_response(monkeypatch):
    settings.LLM_PROVIDER = "ollama"
    settings.LLM_MODEL = "ollama-test"
    settings.LLM_API_KEY = None
    settings.LLM_API_URL = "http://localhost:11434/api/generate"
    settings.LLM_TIMEOUT_SECONDS = 5

    response = FakeResponse(200, {"unexpected": "payload"})

    def fake_async_client(*args, **kwargs):
        return FakeAsyncClient(response=response)

    monkeypatch.setattr("app.services.llm_client.httpx.AsyncClient", fake_async_client)

    answer = await generate_answer("Is this working?", [])
    assert answer.startswith("Thanks for your message:")
    assert "I'm learning to respond better" in answer


@pytest.mark.asyncio
async def test_generate_answer_ollama_fallback_on_http_error(monkeypatch):
    settings.LLM_PROVIDER = "ollama"
    settings.LLM_MODEL = "ollama-test"
    settings.LLM_API_KEY = None
    settings.LLM_API_URL = "http://localhost:11434/api/generate"
    settings.LLM_TIMEOUT_SECONDS = 5

    response = FakeResponse(500, {"error": "server error"})

    def fake_async_client(*args, **kwargs):
        return FakeAsyncClient(response=response)

    monkeypatch.setattr("app.services.llm_client.httpx.AsyncClient", fake_async_client)

    answer = await generate_answer("Why is this failing?", [])
    assert answer.startswith("Thanks for your message:")


@pytest.mark.asyncio
async def test_generate_answer_gemini_success(monkeypatch):
    settings.LLM_PROVIDER = "gemini"
    settings.LLM_MODEL = "gemini-2.0-flash"
    settings.LLM_API_KEY = "fake-key"
    settings.LLM_TIMEOUT_SECONDS = 5

    response = FakeResponse(
        200,
        {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": "Hello from Gemini."}]
                    }
                }
            ]
        },
    )

    def fake_async_client(*args, **kwargs):
        return FakeAsyncClient(response=response)

    monkeypatch.setattr("app.services.llm_client.httpx.AsyncClient", fake_async_client)

    answer = await generate_answer("What is OperaBot?", [])
    assert answer == "Hello from Gemini."

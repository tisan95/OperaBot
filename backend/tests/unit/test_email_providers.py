"""Unit tests for the email provider dispatcher (send_email) and templates."""

import pytest
import app.services.email_service as email_service
from app.config import settings


class _FakeSMTP:
    instances = []

    def __init__(self, host, port, timeout=5):
        self.host = host
        self.port = port
        self.sent = []
        _FakeSMTP.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass

    def send_message(self, msg):
        self.sent.append(msg)


class _FailingSMTP:
    def __init__(self, *a, **kw):
        raise ConnectionRefusedError("no mailhog running")


class _FakeResp:
    def __init__(self, status_code, body):
        self.status_code = status_code
        self._body = body
        self.text = str(body)

    def json(self):
        return self._body


class _FakeHttpClient:
    def __init__(self, response):
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        pass

    async def post(self, url, **kwargs):
        return self._response


def _patch_httpx(monkeypatch, response):
    monkeypatch.setattr(
        "app.services.email_service.httpx.AsyncClient",
        lambda *a, **kw: _FakeHttpClient(response),
    )


# ── MailHog ──────────────────────────────────────────────────────────────────

async def test_mailhog_sends_successfully(monkeypatch):
    settings.EMAIL_PROVIDER = "mailhog"
    _FakeSMTP.instances = []
    monkeypatch.setattr("app.services.email_service.smtplib.SMTP", _FakeSMTP)

    result = await email_service.send_email("user@test.com", "Asunto", "<p>Hola</p>", "Hola")

    assert result is True
    assert len(_FakeSMTP.instances) == 1
    assert _FakeSMTP.instances[0].sent[0]["To"] == "user@test.com"


async def test_mailhog_failure_returns_false_not_raises(monkeypatch):
    settings.EMAIL_PROVIDER = "mailhog"
    monkeypatch.setattr("app.services.email_service.smtplib.SMTP", _FailingSMTP)

    result = await email_service.send_email("user@test.com", "Asunto", "<p>Hola</p>", "Hola")

    assert result is False


# ── Resend ───────────────────────────────────────────────────────────────────

async def test_resend_sends_successfully(monkeypatch):
    settings.EMAIL_PROVIDER = "resend"
    settings.RESEND_API_KEY = "re_fake_key"
    _patch_httpx(monkeypatch, _FakeResp(200, {"id": "abc123"}))

    result = await email_service.send_email("user@test.com", "Asunto", "<p>Hola</p>", "Hola")

    assert result is True


async def test_resend_without_api_key_returns_false(monkeypatch):
    settings.EMAIL_PROVIDER = "resend"
    settings.RESEND_API_KEY = ""

    result = await email_service.send_email("user@test.com", "Asunto", "<p>Hola</p>", "Hola")

    assert result is False


async def test_resend_http_error_returns_false(monkeypatch):
    settings.EMAIL_PROVIDER = "resend"
    settings.RESEND_API_KEY = "re_fake_key"
    _patch_httpx(monkeypatch, _FakeResp(422, {"message": "invalid from"}))

    result = await email_service.send_email("user@test.com", "Asunto", "<p>Hola</p>", "Hola")

    assert result is False


# ── Unknown provider falls back to mailhog ───────────────────────────────────

async def test_unknown_provider_falls_back_to_mailhog(monkeypatch):
    settings.EMAIL_PROVIDER = "some-unknown-provider"
    _FakeSMTP.instances = []
    monkeypatch.setattr("app.services.email_service.smtplib.SMTP", _FakeSMTP)

    result = await email_service.send_email("user@test.com", "Asunto", "<p>Hola</p>", "Hola")

    assert result is True
    assert len(_FakeSMTP.instances) == 1


# ── Use-case templates ────────────────────────────────────────────────────────

async def test_send_welcome_email_calls_dispatcher(monkeypatch):
    captured = {}

    async def _fake_send(to_email, subject, html_body, text_body):
        captured.update(to=to_email, subject=subject, html=html_body, text=text_body)
        return True

    monkeypatch.setattr(email_service, "send_email", _fake_send)

    result = await email_service.send_welcome_email("nuevo@test.com", "Mi Empresa")

    assert result is True
    assert captured["to"] == "nuevo@test.com"
    assert "Mi Empresa" in captured["html"]
    assert "aprobada" in captured["subject"].lower()


async def test_send_ticket_resolved_email_calls_dispatcher(monkeypatch):
    captured = {}

    async def _fake_send(to_email, subject, html_body, text_body):
        captured.update(to=to_email, subject=subject, html=html_body, text=text_body)
        return True

    monkeypatch.setattr(email_service, "send_email", _fake_send)

    result = await email_service.send_ticket_resolved_email(
        "user@test.com", "¿Cómo reinicio la impresora?"
    )

    assert result is True
    assert "my-tickets" in captured["html"]
    assert "impresora" in captured["html"]


async def test_welcome_email_escapes_html_in_company_name(monkeypatch):
    captured = {}

    async def _fake_send(to_email, subject, html_body, text_body):
        captured["html"] = html_body
        return True

    monkeypatch.setattr(email_service, "send_email", _fake_send)

    await email_service.send_welcome_email("x@test.com", "<script>alert(1)</script>")

    assert "<script>" not in captured["html"]

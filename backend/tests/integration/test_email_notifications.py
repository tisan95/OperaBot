"""Integration tests: transactional emails fire on user approval and ticket
resolution, and never break the main flow if sending fails."""

import pytest


# ── User approval → welcome email ────────────────────────────────────────────

async def test_approving_user_sends_welcome_email(client, admin_auth, monkeypatch):
    calls = []

    async def _fake_welcome(to_email, company_name):
        calls.append((to_email, company_name))
        return True

    monkeypatch.setattr("app.api.routes.users.send_welcome_email", _fake_welcome)

    email = "pending-user@test.com"
    company = admin_auth["data"]["company"]["name"]
    r = await client.post("/auth/register", json={
        "email": email, "password": "User1234!", "company_name": company,
    })
    user_id = r.json()["user"]["id"]

    r2 = await client.patch(f"/users/{user_id}/approve", json={"role": "user"},
        cookies=admin_auth["cookies"])
    assert r2.status_code == 200

    assert len(calls) == 1
    assert calls[0][0] == email


async def test_approve_succeeds_even_if_email_fails(client, admin_auth, monkeypatch):
    async def _boom(*a, **kw):
        raise ConnectionError("mailhog down")

    monkeypatch.setattr("app.api.routes.users.send_welcome_email", _boom)

    r = await client.post("/auth/register", json={
        "email": "another@test.com", "password": "User1234!",
        "company_name": admin_auth["data"]["company"]["name"],
    })
    user_id = r.json()["user"]["id"]

    r2 = await client.patch(f"/users/{user_id}/approve", json={"role": "user"},
        cookies=admin_auth["cookies"])
    assert r2.status_code == 200
    assert r2.json()["status"] == "active"


# ── Ticket resolution → notification email ───────────────────────────────────

async def test_resolving_ticket_sends_notification_email(client, admin_auth, user_auth, monkeypatch):
    calls = []

    async def _fake_notify(to_email, question):
        calls.append((to_email, question))
        return True

    monkeypatch.setattr("app.api.routes.tickets.send_ticket_resolved_email", _fake_notify)

    esc = await client.post("/chat/escalate", json={
        "question": "No arranca la impresora",
        "context_summary": "",
        "answers": [],
    }, cookies=user_auth["cookies"])
    ticket_id = esc.json()["ticket_id"]

    r = await client.patch(f"/tickets/{ticket_id}", json={
        "status": "resolved",
        "resolution_message": "<p>Reinicia el driver.</p>",
    }, cookies=admin_auth["cookies"])
    assert r.status_code == 200

    assert len(calls) == 1
    assert calls[0][1] == "No arranca la impresora"


async def test_resolve_succeeds_even_if_email_fails(client, admin_auth, user_auth, monkeypatch):
    async def _boom(*a, **kw):
        raise ConnectionError("mailhog down")

    monkeypatch.setattr("app.api.routes.tickets.send_ticket_resolved_email", _boom)

    esc = await client.post("/chat/escalate", json={
        "question": "Problema de red",
        "context_summary": "",
        "answers": [],
    }, cookies=user_auth["cookies"])
    ticket_id = esc.json()["ticket_id"]

    r = await client.patch(f"/tickets/{ticket_id}", json={
        "status": "resolved",
        "resolution_message": "<p>Solucionado.</p>",
    }, cookies=admin_auth["cookies"])
    assert r.status_code == 200
    assert r.json()["status"] == "resolved"


async def test_moving_to_in_progress_does_not_send_resolution_email(client, admin_auth, user_auth, monkeypatch):
    calls = []

    async def _fake_notify(*a, **kw):
        calls.append(a)
        return True

    monkeypatch.setattr("app.api.routes.tickets.send_ticket_resolved_email", _fake_notify)

    esc = await client.post("/chat/escalate", json={
        "question": "Otro problema",
        "context_summary": "",
        "answers": [],
    }, cookies=user_auth["cookies"])
    ticket_id = esc.json()["ticket_id"]

    r = await client.patch(f"/tickets/{ticket_id}", json={"status": "in_progress"},
        cookies=admin_auth["cookies"])
    assert r.status_code == 200
    assert calls == []


async def test_resolving_twice_only_sends_email_once(client, admin_auth, user_auth, monkeypatch):
    """Editing an already-resolved ticket must not re-trigger the notification."""
    calls = []

    async def _fake_notify(*a, **kw):
        calls.append(a)
        return True

    monkeypatch.setattr("app.api.routes.tickets.send_ticket_resolved_email", _fake_notify)

    esc = await client.post("/chat/escalate", json={
        "question": "Duplicado",
        "context_summary": "",
        "answers": [],
    }, cookies=user_auth["cookies"])
    ticket_id = esc.json()["ticket_id"]

    await client.patch(f"/tickets/{ticket_id}", json={
        "status": "resolved", "resolution_message": "<p>Primera resolución.</p>",
    }, cookies=admin_auth["cookies"])

    await client.patch(f"/tickets/{ticket_id}", json={
        "resolution_message": "<p>Mensaje actualizado.</p>",
    }, cookies=admin_auth["cookies"])

    assert len(calls) == 1

"""Integration tests for ticket endpoints — full lifecycle."""

import pytest


# ── /tickets/my ───────────────────────────────────────────────────────────────

async def test_list_my_tickets_empty(client, user_auth):
    r = await client.get("/tickets/my", cookies=user_auth["cookies"])
    assert r.status_code == 200
    assert r.json() == []


async def test_escalate_then_list_my_tickets(client, user_auth):
    await client.post("/chat/escalate", json={
        "question": "No funciona el sistema",
        "context_summary": "Error al iniciar",
        "answers": [],
    }, cookies=user_auth["cookies"])

    r = await client.get("/tickets/my", cookies=user_auth["cookies"])
    assert r.status_code == 200
    tickets = r.json()
    assert len(tickets) == 1
    assert tickets[0]["question"] == "No funciona el sistema"
    assert tickets[0]["status"] == "open"


# ── GET /tickets/ (admin) ─────────────────────────────────────────────────────

async def test_admin_can_list_all_tickets(client, admin_auth, user_auth):
    await client.post("/chat/escalate", json={
        "question": "Consulta de prueba",
        "context_summary": "",
        "answers": [],
    }, cookies=user_auth["cookies"])

    r = await client.get("/tickets/", cookies=admin_auth["cookies"])
    assert r.status_code == 200
    assert len(r.json()) >= 1


async def test_user_cannot_list_all_tickets(client, user_auth):
    r = await client.get("/tickets/", cookies=user_auth["cookies"])
    assert r.status_code == 403


async def test_admin_filters_tickets_by_status(client, admin_auth, user_auth):
    await client.post("/chat/escalate", json={
        "question": "Problema de acceso",
        "context_summary": "",
        "answers": [],
    }, cookies=user_auth["cookies"])

    r = await client.get("/tickets/?filter_status=open", cookies=admin_auth["cookies"])
    assert r.status_code == 200
    assert all(t["status"] == "open" for t in r.json())


# ── PATCH /tickets/{id} (admin) ───────────────────────────────────────────────

async def test_admin_can_update_ticket_status(client, admin_auth, user_auth):
    esc = await client.post("/chat/escalate", json={
        "question": "Problema X",
        "context_summary": "",
        "answers": [],
    }, cookies=user_auth["cookies"])
    ticket_id = esc.json()["ticket_id"]

    r = await client.patch(f"/tickets/{ticket_id}",
        json={"status": "in_progress"},
        cookies=admin_auth["cookies"])
    assert r.status_code == 200
    assert r.json()["status"] == "in_progress"


async def test_admin_can_resolve_ticket_with_message(client, admin_auth, user_auth):
    esc = await client.post("/chat/escalate", json={
        "question": "Problema Y",
        "context_summary": "",
        "answers": [],
    }, cookies=user_auth["cookies"])
    ticket_id = esc.json()["ticket_id"]

    r = await client.patch(f"/tickets/{ticket_id}", json={
        "status": "resolved",
        "resolution_message": "<p>Resuelto con el paso 3.</p>",
    }, cookies=admin_auth["cookies"])
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "resolved"
    assert data["resolved_at"] is not None
    assert "Resuelto" in data["resolution_message"]


async def test_resolved_ticket_sets_resolved_at(client, admin_auth, user_auth):
    esc = await client.post("/chat/escalate", json={
        "question": "Problema Z",
        "context_summary": "",
        "answers": [],
    }, cookies=user_auth["cookies"])
    ticket_id = esc.json()["ticket_id"]

    r = await client.patch(f"/tickets/{ticket_id}",
        json={"status": "resolved"},
        cookies=admin_auth["cookies"])
    assert r.json()["resolved_at"] is not None


async def test_user_cannot_update_ticket(client, admin_auth, user_auth):
    esc = await client.post("/chat/escalate", json={
        "question": "Problema",
        "context_summary": "",
        "answers": [],
    }, cookies=user_auth["cookies"])
    ticket_id = esc.json()["ticket_id"]

    r = await client.patch(f"/tickets/{ticket_id}",
        json={"status": "resolved"},
        cookies=user_auth["cookies"])
    assert r.status_code == 403


# ── Notes ─────────────────────────────────────────────────────────────────────

async def test_admin_can_add_note(client, admin_auth, user_auth):
    esc = await client.post("/chat/escalate", json={
        "question": "Necesita nota",
        "context_summary": "",
        "answers": [],
    }, cookies=user_auth["cookies"])
    ticket_id = esc.json()["ticket_id"]

    r = await client.post(f"/tickets/{ticket_id}/notes",
        json={"content": "<p>Revisando el servidor</p>"},
        cookies=admin_auth["cookies"])
    assert r.status_code == 201
    data = r.json()
    assert "Revisando" in data["content"]
    assert data["ticket_id"] == ticket_id


async def test_admin_can_list_notes(client, admin_auth, user_auth):
    esc = await client.post("/chat/escalate", json={
        "question": "Con notas",
        "context_summary": "",
        "answers": [],
    }, cookies=user_auth["cookies"])
    ticket_id = esc.json()["ticket_id"]

    await client.post(f"/tickets/{ticket_id}/notes",
        json={"content": "Primera nota"},
        cookies=admin_auth["cookies"])
    await client.post(f"/tickets/{ticket_id}/notes",
        json={"content": "Segunda nota"},
        cookies=admin_auth["cookies"])

    r = await client.get(f"/tickets/{ticket_id}/notes",
        cookies=admin_auth["cookies"])
    assert r.status_code == 200
    assert len(r.json()) == 2


async def test_user_cannot_add_note(client, admin_auth, user_auth):
    esc = await client.post("/chat/escalate", json={
        "question": "Sin nota de usuario",
        "context_summary": "",
        "answers": [],
    }, cookies=user_auth["cookies"])
    ticket_id = esc.json()["ticket_id"]

    r = await client.post(f"/tickets/{ticket_id}/notes",
        json={"content": "Nota no permitida"},
        cookies=user_auth["cookies"])
    assert r.status_code == 403


# ── Archiving ─────────────────────────────────────────────────────────────────

async def test_archive_endpoint_archives_resolved_old_tickets(client, admin_auth, user_auth):
    """Resolved tickets older than retention window get archived."""
    from datetime import timedelta
    from app.db.database import AsyncSessionLocal
    from app.models.ticket import Ticket
    from sqlalchemy import select

    # Create ticket via escalate
    esc = await client.post("/chat/escalate", json={
        "question": "Ticket a archivar",
        "context_summary": "",
        "answers": [],
    }, cookies=user_auth["cookies"])
    ticket_id = esc.json()["ticket_id"]

    # Resolve it
    await client.patch(f"/tickets/{ticket_id}",
        json={"status": "resolved"},
        cookies=admin_auth["cookies"])

    # Backdate resolved_at to exceed retention
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
        t = result.scalar_one()
        from datetime import datetime
        t.resolved_at = datetime.utcnow() - timedelta(days=10)
        await db.commit()

    # Archive
    r = await client.post("/tickets/archive", cookies=admin_auth["cookies"])
    assert r.status_code == 200
    assert r.json()["archived"] >= 1

    # Should not appear in default list
    r2 = await client.get("/tickets/", cookies=admin_auth["cookies"])
    assert not any(t["id"] == ticket_id for t in r2.json())

    # Should appear with include_archived=true
    r3 = await client.get("/tickets/?include_archived=true", cookies=admin_auth["cookies"])
    assert any(t["id"] == ticket_id for t in r3.json())


async def test_archive_does_not_archive_recent_resolved_tickets(client, admin_auth, user_auth):
    esc = await client.post("/chat/escalate", json={
        "question": "Ticket reciente resuelto",
        "context_summary": "",
        "answers": [],
    }, cookies=user_auth["cookies"])
    ticket_id = esc.json()["ticket_id"]

    await client.patch(f"/tickets/{ticket_id}",
        json={"status": "resolved"},
        cookies=admin_auth["cookies"])

    r = await client.post("/tickets/archive", cookies=admin_auth["cookies"])
    assert r.status_code == 200
    assert r.json()["archived"] == 0


async def test_company_settings_default_retention(client, admin_auth):
    r = await client.get("/tickets/settings", cookies=admin_auth["cookies"])
    assert r.status_code == 200
    assert r.json()["ticket_retention_days"] == 7


async def test_company_settings_update_retention(client, admin_auth):
    r = await client.patch("/tickets/settings",
        json={"ticket_retention_days": 30},
        cookies=admin_auth["cookies"])
    assert r.status_code == 200
    assert r.json()["ticket_retention_days"] == 30

    r2 = await client.get("/tickets/settings", cookies=admin_auth["cookies"])
    assert r2.json()["ticket_retention_days"] == 30


async def test_company_settings_invalid_retention(client, admin_auth):
    r = await client.patch("/tickets/settings",
        json={"ticket_retention_days": 99},
        cookies=admin_auth["cookies"])
    assert r.status_code == 400


# ── Multi-tenant isolation ────────────────────────────────────────────────────

async def test_admin_cannot_see_other_company_tickets(client, admin_auth):
    """Admin of Co-A should not see tickets from Co-B."""
    import uuid
    u = uuid.uuid4().hex[:8]
    # Register Co-B and create a ticket
    r_b = await client.post("/auth/register", json={
        "email": f"admin-{u}@cob.com", "password": "Admin1234!",
        "company_name": f"Co-B-{u}",
    })
    cookies_b = dict(r_b.cookies)
    await client.post("/chat/escalate", json={
        "question": "Ticket de Co-B",
        "context_summary": "",
        "answers": [],
    }, cookies=cookies_b)

    # Co-A admin should see 0 tickets
    r = await client.get("/tickets/", cookies=admin_auth["cookies"])
    assert r.status_code == 200
    assert not any(t["question"] == "Ticket de Co-B" for t in r.json())

"""Integration tests for FAQ endpoints."""

import pytest


# ── CRUD (admin) ──────────────────────────────────────────────────────────────

async def test_admin_can_create_faq(client, admin_auth):
    r = await client.post("/faqs", json={
        "question": "¿Qué es OperaBot?",
        "answer": "Un asistente de conocimiento.",
        "category": "General",
    }, cookies=admin_auth["cookies"])
    assert r.status_code == 201
    data = r.json()
    assert data["question"] == "¿Qué es OperaBot?"
    assert "id" in data


async def test_admin_can_list_faqs(client, admin_auth):
    await client.post("/faqs", json={
        "question": "¿Cómo inicio sesión?",
        "answer": "Con tu email y contraseña.",
        "category": "Acceso",
    }, cookies=admin_auth["cookies"])

    r = await client.get("/faqs", cookies=admin_auth["cookies"])
    assert r.status_code == 200
    assert len(r.json()) >= 1


async def test_admin_can_update_faq(client, admin_auth):
    create = await client.post("/faqs", json={
        "question": "Pregunta original",
        "answer": "Respuesta original",
        "category": "Test",
    }, cookies=admin_auth["cookies"])
    faq_id = create.json()["id"]

    r = await client.put(f"/faqs/{faq_id}", json={
        "question": "Pregunta actualizada",
        "answer": "Respuesta actualizada",
        "category": "Test",
    }, cookies=admin_auth["cookies"])
    assert r.status_code == 200
    assert r.json()["question"] == "Pregunta actualizada"


async def test_admin_can_delete_faq(client, admin_auth):
    create = await client.post("/faqs", json={
        "question": "Para borrar",
        "answer": "Se borrará",
        "category": "Test",
    }, cookies=admin_auth["cookies"])
    faq_id = create.json()["id"]

    r = await client.delete(f"/faqs/{faq_id}", cookies=admin_auth["cookies"])
    assert r.status_code == 204


# ── Auth & role enforcement ───────────────────────────────────────────────────

async def test_authenticated_user_can_list_faqs(client, user_auth):
    r = await client.get("/faqs", cookies=user_auth["cookies"])
    assert r.status_code == 200


async def test_user_cannot_create_faq(client, user_auth):
    r = await client.post("/faqs", json={
        "question": "Pregunta de usuario",
        "answer": "No debería poder",
        "category": "Test",
    }, cookies=user_auth["cookies"])
    assert r.status_code == 403


async def test_unauthenticated_cannot_list_faqs(client):
    r = await client.get("/faqs")
    assert r.status_code == 401


# ── Multi-tenant isolation ────────────────────────────────────────────────────

async def test_faqs_are_isolated_per_company(client, admin_auth):
    """FAQs created by Co-A should not be visible to Co-B."""
    await client.post("/faqs", json={
        "question": "FAQ de Co-A", "answer": "Respuesta", "category": "Test"
    }, cookies=admin_auth["cookies"])

    # Register a second independent company
    r_b = await client.post("/auth/register", json={
        "email": "admin2@cob.com", "password": "Admin1234!", "company_name": "Co-B-Isolated",
    })
    cookies_b = dict(r_b.cookies)

    r = await client.get("/faqs", cookies=cookies_b)
    assert r.status_code == 200
    assert not any(f["question"] == "FAQ de Co-A" for f in r.json())

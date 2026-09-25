"""Integration tests for chat session management."""

import pytest


# ── Create & list ─────────────────────────────────────────────────────────────

async def test_create_session_returns_201(client, admin_auth):
    r = await client.post("/chat/sessions", cookies=admin_auth["cookies"])
    assert r.status_code == 201
    data = r.json()
    assert "id" in data
    assert data["title"] is None
    assert "created_at" in data
    assert "updated_at" in data


async def test_list_sessions_empty_initially(client, admin_auth):
    r = await client.get("/chat/sessions", cookies=admin_auth["cookies"])
    assert r.status_code == 200
    assert r.json() == []


async def test_list_sessions_shows_created(client, admin_auth):
    await client.post("/chat/sessions", cookies=admin_auth["cookies"])
    await client.post("/chat/sessions", cookies=admin_auth["cookies"])
    r = await client.get("/chat/sessions", cookies=admin_auth["cookies"])
    assert r.status_code == 200
    assert len(r.json()) == 2


async def test_list_sessions_ordered_by_updated_at_desc(client, admin_auth):
    r1 = await client.post("/chat/sessions", cookies=admin_auth["cookies"])
    r2 = await client.post("/chat/sessions", cookies=admin_auth["cookies"])
    s1_id, s2_id = r1.json()["id"], r2.json()["id"]

    r = await client.get("/chat/sessions", cookies=admin_auth["cookies"])
    ids = [s["id"] for s in r.json()]
    # Most-recently created (s2) should appear first
    assert ids[0] == s2_id
    assert ids[1] == s1_id


# ── 5-session limit & auto-archiving ─────────────────────────────────────────

async def test_creating_sixth_session_archives_oldest(client, admin_auth):
    """Creating a 6th session must auto-archive the oldest one."""
    session_ids = []
    for _ in range(5):
        r = await client.post("/chat/sessions", cookies=admin_auth["cookies"])
        assert r.status_code == 201
        session_ids.append(r.json()["id"])

    # All 5 should be active
    r = await client.get("/chat/sessions", cookies=admin_auth["cookies"])
    assert len(r.json()) == 5

    # Create the 6th
    r6 = await client.post("/chat/sessions", cookies=admin_auth["cookies"])
    assert r6.status_code == 201

    # Now only 5 active sessions should remain
    r = await client.get("/chat/sessions", cookies=admin_auth["cookies"])
    active = r.json()
    assert len(active) == 5

    active_ids = {s["id"] for s in active}
    # The oldest (first created) must have been archived — it shouldn't appear
    assert session_ids[0] not in active_ids
    # The newest (6th) must be present
    assert r6.json()["id"] in active_ids


async def test_limit_applied_on_each_creation(client, admin_auth):
    """After the limit, each new session archives exactly one old one."""
    for _ in range(6):
        await client.post("/chat/sessions", cookies=admin_auth["cookies"])

    r = await client.get("/chat/sessions", cookies=admin_auth["cookies"])
    assert len(r.json()) == 5

    await client.post("/chat/sessions", cookies=admin_auth["cookies"])
    r = await client.get("/chat/sessions", cookies=admin_auth["cookies"])
    assert len(r.json()) == 5


# ── Auto-naming ───────────────────────────────────────────────────────────────

async def test_first_message_sets_title(client, admin_auth, admin_session):
    """Sending the first message auto-names the session from the first 40 chars."""
    msg = "Cómo configuro el acceso remoto al servidor"
    await client.post("/chat/messages",
        json={"message": msg, "session_id": admin_session},
        cookies=admin_auth["cookies"])

    r = await client.get("/chat/sessions", cookies=admin_auth["cookies"])
    session = next(s for s in r.json() if s["id"] == admin_session)
    expected = msg[:40].strip() + "…"  # message is >40 chars so ellipsis is appended
    assert session["title"] == expected


async def test_long_message_gets_ellipsis(client, admin_auth, admin_session):
    """Messages longer than 40 chars get truncated with an ellipsis."""
    msg = "Esta es una pregunta muy larga que supera los cuarenta caracteres con creces"
    await client.post("/chat/messages",
        json={"message": msg, "session_id": admin_session},
        cookies=admin_auth["cookies"])

    r = await client.get("/chat/sessions", cookies=admin_auth["cookies"])
    session = next(s for s in r.json() if s["id"] == admin_session)
    title = session["title"]
    assert title is not None
    assert len(title) <= 41  # 40 chars + "…"
    assert title.endswith("…")


async def test_second_message_does_not_rename_session(client, admin_auth, admin_session):
    """Once a session has a title, subsequent messages don't overwrite it."""
    first = "Primera pregunta para nombrar la sesión"
    second = "Segunda pregunta completamente diferente"

    await client.post("/chat/messages",
        json={"message": first, "session_id": admin_session},
        cookies=admin_auth["cookies"])
    await client.post("/chat/messages",
        json={"message": second, "session_id": admin_session},
        cookies=admin_auth["cookies"])

    r = await client.get("/chat/sessions", cookies=admin_auth["cookies"])
    session = next(s for s in r.json() if s["id"] == admin_session)
    assert session["title"] == first[:40].strip()


# ── Session isolation ─────────────────────────────────────────────────────────

async def test_user_cannot_see_other_users_sessions(client, admin_auth, user_auth):
    """Sessions created by admin are not visible to a different user."""
    await client.post("/chat/sessions", cookies=admin_auth["cookies"])

    r = await client.get("/chat/sessions", cookies=user_auth["cookies"])
    assert r.status_code == 200
    assert r.json() == []


async def test_user_cannot_post_to_other_users_session(client, admin_auth, user_auth):
    """A user cannot post messages into a session that belongs to another user."""
    r = await client.post("/chat/sessions", cookies=admin_auth["cookies"])
    admin_session_id = r.json()["id"]

    r2 = await client.post("/chat/messages",
        json={"message": "intento de acceso cruzado", "session_id": admin_session_id},
        cookies=user_auth["cookies"])
    assert r2.status_code == 404


async def test_user_cannot_get_messages_from_other_users_session(client, admin_auth, user_auth, admin_session):
    """A user cannot read messages from a session they don't own."""
    r = await client.get(f"/chat/sessions/{admin_session}/messages",
        cookies=user_auth["cookies"])
    assert r.status_code == 404


async def test_user_cannot_delete_other_users_session(client, admin_auth, user_auth, admin_session):
    """A user cannot delete a session belonging to another user."""
    r = await client.delete(f"/chat/sessions/{admin_session}",
        cookies=user_auth["cookies"])
    assert r.status_code == 404


# ── Get session messages ──────────────────────────────────────────────────────

async def test_get_session_messages_empty(client, admin_auth, admin_session):
    r = await client.get(f"/chat/sessions/{admin_session}/messages",
        cookies=admin_auth["cookies"])
    assert r.status_code == 200
    assert r.json() == []


async def test_get_session_messages_after_chat(client, admin_auth, admin_session):
    await client.post("/chat/messages",
        json={"message": "hola", "session_id": admin_session},
        cookies=admin_auth["cookies"])
    await client.post("/chat/messages",
        json={"message": "adiós", "session_id": admin_session},
        cookies=admin_auth["cookies"])

    r = await client.get(f"/chat/sessions/{admin_session}/messages",
        cookies=admin_auth["cookies"])
    assert r.status_code == 200
    msgs = r.json()
    assert len(msgs) == 2
    assert msgs[0]["user_message"] == "hola"
    assert msgs[1]["user_message"] == "adiós"


async def test_messages_scoped_to_session(client, admin_auth):
    """Messages from session A don't appear when querying session B."""
    r1 = await client.post("/chat/sessions", cookies=admin_auth["cookies"])
    r2 = await client.post("/chat/sessions", cookies=admin_auth["cookies"])
    s1, s2 = r1.json()["id"], r2.json()["id"]

    await client.post("/chat/messages",
        json={"message": "mensaje en sesión uno", "session_id": s1},
        cookies=admin_auth["cookies"])

    r = await client.get(f"/chat/sessions/{s2}/messages",
        cookies=admin_auth["cookies"])
    assert r.json() == []


# ── Delete session ────────────────────────────────────────────────────────────

async def test_delete_session_removes_it(client, admin_auth, admin_session):
    r = await client.delete(f"/chat/sessions/{admin_session}",
        cookies=admin_auth["cookies"])
    assert r.status_code == 204

    r2 = await client.get("/chat/sessions", cookies=admin_auth["cookies"])
    assert all(s["id"] != admin_session for s in r2.json())


async def test_delete_session_removes_its_messages(client, admin_auth, admin_session):
    """Deleting a session cascades to its messages."""
    await client.post("/chat/messages",
        json={"message": "hola", "session_id": admin_session},
        cookies=admin_auth["cookies"])

    await client.delete(f"/chat/sessions/{admin_session}",
        cookies=admin_auth["cookies"])

    # The session is gone; its messages endpoint should return 404
    r = await client.get(f"/chat/sessions/{admin_session}/messages",
        cookies=admin_auth["cookies"])
    assert r.status_code == 404


async def test_delete_nonexistent_session_returns_404(client, admin_auth):
    r = await client.delete("/chat/sessions/999999",
        cookies=admin_auth["cookies"])
    assert r.status_code == 404


# ── Auth ──────────────────────────────────────────────────────────────────────

async def test_create_session_requires_auth(client):
    r = await client.post("/chat/sessions")
    assert r.status_code == 401


async def test_list_sessions_requires_auth(client):
    r = await client.get("/chat/sessions")
    assert r.status_code == 401

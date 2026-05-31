"""Integration tests for document endpoints (upload, preview, download, roles)."""

import os
import tempfile
import pytest
import pytest_asyncio


# ── Fixture: temp PDF + DB record ─────────────────────────────────────────────

@pytest_asyncio.fixture
async def test_document(admin_auth):
    """Create a temp PDF on disk and a Document row in the DB. Returns (doc_id, path)."""
    # Create a minimal PDF-like file (enough for FileResponse to serve)
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp.write(b"%PDF-1.4 test document content")
    tmp.flush()
    tmp.close()
    tmp_path = tmp.name

    company_id = admin_auth["data"]["company"]["id"]

    from app.db.database import AsyncSessionLocal
    from app.models.document import Document

    async with AsyncSessionLocal() as db:
        doc = Document(
            company_id=company_id,
            filename="test.pdf",
            content_type="application/pdf",
            file_size=os.path.getsize(tmp_path),
            file_path=tmp_path,
            upload_status="completed",
            vector_count=0,
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        doc_id = doc.id

    yield doc_id, tmp_path

    try:
        os.unlink(tmp_path)
    except FileNotFoundError:
        pass


# ── Upload ────────────────────────────────────────────────────────────────────

async def test_user_cannot_upload_document(client, user_auth):
    content = b"%PDF-1.4 minimal"
    r = await client.post(
        "/documents/upload",
        files={"file": ("test.pdf", content, "application/pdf")},
        cookies=user_auth["cookies"],
    )
    assert r.status_code == 403


async def test_unauthenticated_cannot_upload(client):
    content = b"%PDF-1.4 minimal"
    r = await client.post(
        "/documents/upload",
        files={"file": ("test.pdf", content, "application/pdf")},
    )
    assert r.status_code == 401


# ── List ──────────────────────────────────────────────────────────────────────

async def test_admin_can_list_documents_empty(client, admin_auth):
    r = await client.get("/documents/", cookies=admin_auth["cookies"])
    assert r.status_code == 200
    assert isinstance(r.json(), list)


async def test_user_cannot_list_documents(client, user_auth):
    r = await client.get("/documents/", cookies=user_auth["cookies"])
    assert r.status_code == 403


# ── Preview ───────────────────────────────────────────────────────────────────

async def test_admin_can_preview_document(client, admin_auth, test_document):
    doc_id, _ = test_document
    r = await client.get(f"/documents/{doc_id}/preview",
        cookies=admin_auth["cookies"])
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"


async def test_user_can_preview_document(client, user_auth, test_document, admin_auth):
    doc_id, _ = test_document
    r = await client.get(f"/documents/{doc_id}/preview",
        cookies=user_auth["cookies"])
    assert r.status_code == 200


async def test_unauthenticated_cannot_preview(test_document, admin_auth):
    doc_id, _ = test_document
    # Use a fresh client (no cookie jar from admin_auth)
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as fresh:
        r = await fresh.get(f"/documents/{doc_id}/preview")
    assert r.status_code == 401


async def test_preview_missing_document_returns_404(client, admin_auth):
    r = await client.get("/documents/99999/preview",
        cookies=admin_auth["cookies"])
    assert r.status_code == 404


# ── Download ──────────────────────────────────────────────────────────────────

async def test_admin_can_download_document(client, admin_auth, test_document):
    doc_id, _ = test_document
    r = await client.get(f"/documents/{doc_id}/download",
        cookies=admin_auth["cookies"])
    assert r.status_code == 200
    assert "attachment" in r.headers.get("content-disposition", "")


async def test_user_cannot_download_document(client, user_auth, test_document, admin_auth):
    doc_id, _ = test_document
    r = await client.get(f"/documents/{doc_id}/download",
        cookies=user_auth["cookies"])
    assert r.status_code == 403


async def test_unauthenticated_cannot_download(test_document, admin_auth):
    doc_id, _ = test_document
    # Use a fresh client (no cookie jar from admin_auth)
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as fresh:
        r = await fresh.get(f"/documents/{doc_id}/download")
    assert r.status_code == 401

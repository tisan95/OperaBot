"""Document upload and management endpoints."""

import os
import logging
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.document import Document
from app.services.document_service import document_service
from app.services.qdrant_service import qdrant_service
from app.api.dependencies import get_current_company_id, require_admin
from app.models.user import User
from app.api.schemas.document import DocumentUploadResponse, DocumentList

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Upload ────────────────────────────────────────────────────────────────────

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> DocumentUploadResponse:
    """Upload and process a PDF document (admin only)."""
    company_id = str(current_user.company_id)
    try:
        document = await document_service.process_upload(
            file=file,
            filename=file.filename,
            content_type=file.content_type,
            file_size=file.size,
            company_id=company_id,
            db=db,
        )
        return DocumentUploadResponse(
            id=document.id,
            filename=document.filename,
            status=document.upload_status,
            vector_count=document.vector_count,
            message="Document uploaded and processed successfully",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


# ── List ──────────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[DocumentList])
async def get_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> List[DocumentList]:
    """List all documents for the current company (admin only)."""
    company_id = str(current_user.company_id)
    try:
        documents = await document_service.get_company_documents(company_id, db)
        return [
            DocumentList(
                id=doc.id,
                filename=doc.filename,
                content_type=doc.content_type,
                file_size=doc.file_size,
                upload_status=doc.upload_status,
                vector_count=doc.vector_count,
                created_at=doc.created_at.isoformat(),
            )
            for doc in documents
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve documents: {str(e)}")


# ── Preview / Download ────────────────────────────────────────────────────────

def _get_document_file(doc: Document) -> Path:
    """Validate that a document has a stored file and return its path."""
    if not doc.file_path:
        raise HTTPException(
            status_code=404,
            detail="Este documento no tiene archivo almacenado (fue subido antes de esta funcionalidad).",
        )
    path = Path(doc.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="El archivo no existe en el servidor.")
    return path


@router.get("/{document_id}/preview")
async def preview_document(
    document_id: int,
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Stream PDF inline for in-browser preview. Accessible by any authenticated user."""
    doc = await document_service.get_document(document_id, company_id, db)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado.")

    path = _get_document_file(doc)
    safe_name = doc.filename.replace('"', "")

    return FileResponse(
        path=str(path),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{safe_name}"',
            "Cache-Control": "private, max-age=3600",
        },
    )


@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Force-download PDF. Admin and super_admin only."""
    company_id = str(current_user.company_id)
    doc = await document_service.get_document(document_id, company_id, db)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado.")

    path = _get_document_file(doc)
    safe_name = doc.filename.replace('"', "")

    return FileResponse(
        path=str(path),
        media_type="application/pdf",
        filename=safe_name,
        headers={
            "Content-Disposition": f'attachment; filename="{safe_name}"',
        },
    )


# ── Delete ────────────────────────────────────────────────────────────────────

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    """Delete a document, its file and its vectors (admin only)."""
    company_id = str(current_user.company_id)
    try:
        try:
            logger.info(f"Deleting vectors for document {document_id}")
            qdrant_service.delete_document_vectors(document_id)
        except Exception as e:
            logger.warning(f"Failed to delete Qdrant vectors for {document_id}: {e}")

        success = await document_service.delete_document(document_id, company_id, db)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")

        return {"message": "Document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete failed for document {document_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

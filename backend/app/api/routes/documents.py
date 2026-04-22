"""Document upload and management endpoints."""

from typing import List
import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.document import Document
from app.services.document_service import document_service
from app.services.qdrant_service import qdrant_service
from app.api.dependencies import get_current_company_id
from app.api.schemas.document import DocumentUploadResponse, DocumentList

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    company_id: str = Depends(get_current_company_id)
) -> DocumentUploadResponse:
    """Upload and process a PDF document."""
    try:
        # Process the upload
        document = await document_service.process_upload(
            file=file,
            filename=file.filename,
            content_type=file.content_type,
            file_size=file.size,
            company_id=company_id,
            db=db
        )

        return DocumentUploadResponse(
            id=document.id,
            filename=document.filename,
            status=document.upload_status,
            vector_count=document.vector_count,
            message="Document uploaded and processed successfully"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/", response_model=List[DocumentList])
async def get_documents(
    db: AsyncSession = Depends(get_db),
    company_id: str = Depends(get_current_company_id)
) -> List[DocumentList]:
    """Get all documents for the current company."""
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
                created_at=doc.created_at.isoformat()
            )
            for doc in documents
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve documents: {str(e)}")


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    company_id: str = Depends(get_current_company_id)
) -> dict:
    """Delete a document and its associated vectors."""
    try:
        # 1. Delete vectors from Qdrant first
        try:
            logger.info(f"🗑️ Deleting vectors for document id={document_id} from Qdrant")
            qdrant_service.delete_document_vectors(document_id)
        except Exception as q_err:
            logger.warning(f"⚠️ Failed to delete vectors in Qdrant for document {document_id}: {q_err}")

        # 2. Delete document from PostgreSQL
        success = await document_service.delete_document(document_id, company_id, db)

        if not success:
            raise HTTPException(status_code=404, detail="Document not found")

        logger.info(f"✅ Document id={document_id} deleted successfully from DB and Qdrant")
        return {"message": "Document deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Delete failed for document {document_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
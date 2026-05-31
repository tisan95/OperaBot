"""Document upload and processing service."""

import logging
import os
import tempfile
from typing import List, Dict, Any
from pathlib import Path
from PyPDF2 import PdfReader
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.services.qdrant_service import qdrant_service
from app.config import settings

logger = logging.getLogger(__name__)

# Ensure storage root exists at import time
_STORAGE_ROOT = Path(settings.DOCUMENTS_STORAGE_PATH)
_STORAGE_ROOT.mkdir(parents=True, exist_ok=True)


class DocumentService:
    """Service for handling document uploads and processing."""

    def __init__(self):
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_types = ["application/pdf"]
        self.chunk_size = 1000
        self.chunk_overlap = 200

    async def process_upload(
        self,
        file,
        filename: str,
        content_type: str,
        file_size: int,
        company_id: str,
        db: AsyncSession,
    ) -> Document:
        """Process an uploaded file, store it, and vectorize its content."""
        self._validate_file(filename, content_type, file_size)

        # Read all bytes once — the stream can only be read once
        file_bytes = await file.read()

        # Create document record first (need the ID for the file path)
        document = Document(
            company_id=company_id,
            filename=filename,
            content_type=content_type,
            file_size=file_size,
            upload_status="processing",
        )
        db.add(document)
        await db.commit()
        await db.refresh(document)

        try:
            # Persist PDF to disk
            file_path = self._save_pdf(file_bytes, company_id, document.id, filename)

            # Extract text from the bytes we already have
            extracted_text = self._extract_text_from_bytes(file_bytes, filename)

            # Split into chunks and vectorize
            chunks = self._split_text_into_chunks(extracted_text)
            vector_count = await qdrant_service.store_document_chunks(
                document_id=document.id,
                company_id=company_id,
                chunks=chunks,
                metadata={
                    "filename": filename,
                    "content_type": content_type,
                    "file_size": file_size,
                },
            )

            document.file_path = str(file_path)
            document.extracted_text = extracted_text
            document.vector_count = vector_count
            document.upload_status = "completed"
            await db.commit()
            await db.refresh(document)

            logger.info(f"Processed document {document.id}: {filename} → {file_path}")
            return document

        except Exception as e:
            document.upload_status = "failed"
            await db.commit()
            logger.error(f"Failed to process document {document.id}: {e}")
            raise

    def _validate_file(self, filename: str, content_type: str, file_size: int):
        if content_type not in self.allowed_types:
            raise ValueError(f"Tipo de archivo no soportado: {content_type}. Solo se aceptan PDFs.")
        if file_size > self.max_file_size:
            raise ValueError(f"Archivo demasiado grande: {file_size} bytes. Máximo {self.max_file_size} bytes.")
        if not filename.lower().endswith(".pdf"):
            raise ValueError("El archivo debe tener extensión .pdf")

    def _save_pdf(self, file_bytes: bytes, company_id: str, document_id: int, filename: str) -> Path:
        """Save PDF bytes to persistent storage and return the path."""
        safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in filename)
        company_dir = _STORAGE_ROOT / str(company_id)
        company_dir.mkdir(parents=True, exist_ok=True)
        dest = company_dir / f"{document_id}_{safe_name}"
        dest.write_bytes(file_bytes)
        return dest

    def _extract_text_from_bytes(self, file_bytes: bytes, filename: str = "document.pdf") -> str:
        """Extract text from PDF bytes using a temporary file."""
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name

            reader = PdfReader(tmp_path)
            text = "\n".join(
                page.extract_text() or "" for page in reader.pages
            ).strip()

            if not text:
                raise ValueError("No se pudo extraer texto del PDF")

            logger.info(f"Extracted {len(text)} chars from {filename}")
            return text

        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            raise ValueError(f"No se pudo extraer texto del PDF: {str(e)}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def _split_text_into_chunks(self, text: str) -> List[str]:
        if not text:
            return []
        chunks, start = [], 0
        while start < len(text):
            end = start + self.chunk_size
            if end < len(text):
                for ending in (". ", "! ", "? ", "\n"):
                    pos = text.rfind(ending, max(start, end - 100), end)
                    if pos != -1:
                        end = pos + len(ending)
                        break
                else:
                    sp = text.rfind(" ", max(start, end - 50), end)
                    if sp != -1:
                        end = sp
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = max(start + 1, end - self.chunk_overlap)
        return chunks

    async def get_company_documents(self, company_id: str, db: AsyncSession) -> List[Document]:
        from sqlalchemy import select
        result = await db.execute(select(Document).where(Document.company_id == company_id))
        return result.scalars().all()

    async def get_document(self, document_id: int, company_id: str, db: AsyncSession):
        from sqlalchemy import select
        result = await db.execute(
            select(Document).where(Document.id == document_id, Document.company_id == company_id)
        )
        return result.scalar_one_or_none()

    async def delete_document(self, document_id: int, company_id: str, db: AsyncSession) -> bool:
        doc = await self.get_document(document_id, company_id, db)
        if not doc:
            return False

        # Remove file from disk if present
        if doc.file_path and os.path.exists(doc.file_path):
            try:
                os.unlink(doc.file_path)
            except OSError as e:
                logger.warning(f"Could not delete file {doc.file_path}: {e}")

        qdrant_service.delete_document_vectors(document_id)
        await db.delete(doc)
        await db.commit()
        logger.info(f"Deleted document {document_id} for company {company_id}")
        return True


document_service = DocumentService()

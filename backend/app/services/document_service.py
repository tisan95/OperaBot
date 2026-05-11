"""Document upload and processing service."""

import logging
import os
import tempfile
from typing import List, Dict, Any
from pathlib import Path
from PyPDF2 import PdfReader
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

from app.models.document import Document
from app.services.qdrant_service import qdrant_service

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for handling document uploads and processing."""

    def __init__(self):
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_types = ["application/pdf"]
        self.chunk_size = 1000  # Characters per chunk
        self.chunk_overlap = 200  # Overlap between chunks

    async def process_upload(self, file, filename: str, content_type: str,
                           file_size: int, company_id: str, db: AsyncSession) -> Document:
        """Process an uploaded file and store it.

        Args:
            file: Uploaded file object
            filename: Original filename
            content_type: MIME type
            file_size: File size in bytes
            company_id: Company ID
            db: Database session

        Returns:
            Created Document instance
        """
        # Validate file
        self._validate_file(filename, content_type, file_size)

        # Create document record
        document = Document(
            company_id=company_id,
            filename=filename,
            content_type=content_type,
            file_size=file_size,
            upload_status="processing"
        )

        db.add(document)
        await db.commit()
        await db.refresh(document)

        try:
            # Extract text from PDF
            extracted_text = await self._extract_text_from_pdf(file)

            # Split into chunks
            chunks = self._split_text_into_chunks(extracted_text)

            # Store vectors in Qdrant
            vector_count = await qdrant_service.store_document_chunks(
                document_id=document.id,
                company_id=company_id,
                chunks=chunks,
                metadata={
                    "filename": filename,
                    "content_type": content_type,
                    "file_size": file_size
                }
            )

            # Update document record
            document.extracted_text = extracted_text
            document.vector_count = vector_count
            document.upload_status = "completed"

            await db.commit()
            await db.refresh(document)

            logger.info(f"Successfully processed document {document.id}: {filename}")
            return document

        except Exception as e:
            # Mark as failed
            document.upload_status = "failed"
            await db.commit()

            logger.error(f"Failed to process document {document.id}: {e}")
            raise

    def _validate_file(self, filename: str, content_type: str, file_size: int):
        """Validate uploaded file."""
        if content_type not in self.allowed_types:
            raise ValueError(f"Unsupported file type: {content_type}. Only PDF files are allowed.")

        if file_size > self.max_file_size:
            raise ValueError(f"File too large: {file_size} bytes. Maximum size is {self.max_file_size} bytes.")

        if not filename.lower().endswith('.pdf'):
            raise ValueError("File must have .pdf extension")

    async def _extract_text_from_pdf(self, file) -> str:
        """Extract text content from PDF file."""
        try:
            # Save file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name

            try:
                # Extract text using PyPDF2
                reader = PdfReader(temp_file_path)
                text = ""

                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

                if not text.strip():
                    raise ValueError("No text could be extracted from PDF")

                logger.info(f"Extracted {len(text)} characters from PDF")
                return text.strip()

            finally:
                # Clean up temp file
                os.unlink(temp_file_path)

        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

    def _split_text_into_chunks(self, text: str) -> List[str]:
        """Split text into overlapping chunks for embedding."""
        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # If we're not at the end, try to break at a sentence or word boundary
            if end < len(text):
                # Look for sentence endings within the last 100 characters
                sentence_endings = ['. ', '! ', '? ', '\n']
                break_pos = end

                for ending in sentence_endings:
                    pos = text.rfind(ending, max(start, end - 100), end)
                    if pos != -1:
                        break_pos = pos + len(ending)
                        break

                # If no sentence ending found, break at word boundary
                if break_pos == end:
                    space_pos = text.rfind(' ', max(start, end - 50), end)
                    if space_pos != -1:
                        break_pos = space_pos

                end = break_pos

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move start position with overlap
            start = max(start + 1, end - self.chunk_overlap)

        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks

    async def get_company_documents(self, company_id: str, db: AsyncSession) -> List[Document]:
        """Get all documents for a company."""
        from sqlalchemy import select

        result = await db.execute(
            select(Document).where(Document.company_id == company_id)
        )
        return result.scalars().all()

    async def delete_document(self, document_id: int, company_id: str, db: AsyncSession) -> bool:
        """Delete a document and its vectors."""
        from sqlalchemy import select

        # Get document
        result = await db.execute(
            select(Document).where(
                Document.id == document_id,
                Document.company_id == company_id
            )
        )
        document = result.scalars().first()

        if not document:
            return False

        # Delete vectors from Qdrant
        qdrant_service.delete_document_vectors(document_id)

        # Delete from database
        await db.delete(document)
        await db.commit()

        logger.info(f"Deleted document {document_id} for company {company_id}")
        return True


# Global instance
document_service = DocumentService()
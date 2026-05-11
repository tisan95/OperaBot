"""Document API schemas."""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DocumentBase(BaseModel):
    """Base document schema."""
    filename: str
    content_type: str
    file_size: int
    upload_status: str
    vector_count: int
    created_at: datetime


class DocumentRead(DocumentBase):
    """Document read schema."""
    id: int

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    """Response for document upload."""
    id: int
    filename: str
    status: str
    vector_count: int
    message: str


class DocumentList(BaseModel):
    """Document list item."""
    id: int
    filename: str
    content_type: str
    file_size: int
    upload_status: str
    vector_count: int
    created_at: str
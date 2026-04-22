"""Document model for uploaded files."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base, GUID


class Document(Base):
    """Document entry model for uploaded files."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(GUID(), ForeignKey("companies.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    extracted_text = Column(Text, nullable=True)  # Extracted text from PDF
    vector_count = Column(Integer, default=0)  # Number of vectors stored in Qdrant
    upload_status = Column(String(50), default="processing")  # processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    company = relationship("Company", back_populates="documents")

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, filename={self.filename}, company_id={self.company_id}, status={self.upload_status})>"
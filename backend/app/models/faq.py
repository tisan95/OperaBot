"""FAQ model."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base, GUID


class FAQ(Base):
    """FAQ entry model."""

    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(GUID(), ForeignKey("companies.id"), nullable=False, index=True)
    question = Column(String(1024), nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    company = relationship("Company", back_populates="faqs")

    def __repr__(self) -> str:
        return f"<FAQ(id={self.id}, question={self.question}, company_id={self.company_id})>"

"""Chat message model."""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base, GUID


class ChatMessage(Base):
    """Chat message record for persisted conversation history."""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(GUID(), ForeignKey("companies.id"), nullable=False, index=True)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    user_message = Column(Text, nullable=False)
    bot_message = Column(Text, nullable=False)
    is_fallback = Column(Boolean, default=False, nullable=False)
    confidence = Column(Float, default=0.0, nullable=False)  # Confidence score 0.0-1.0
    rating = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="chat_messages")
    company = relationship("Company", back_populates="chat_messages")

    def __repr__(self) -> str:
        return (
            f"<ChatMessage(id={self.id}, user_id={self.user_id}, "
            f"company_id={self.company_id})>"
        )

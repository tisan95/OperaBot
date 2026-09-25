"""Chat session model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base, GUID


class ChatSession(Base):
    """A named conversation thread for a user. Holds many ChatMessages."""

    __tablename__ = "chat_sessions"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(GUID(), ForeignKey("users.id"),    nullable=False, index=True)
    company_id = Column(GUID(), ForeignKey("companies.id"), nullable=False, index=True)
    # Auto-filled with the first 40 chars of the first user message
    title      = Column(String(100), nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at  = Column(DateTime, default=datetime.utcnow, nullable=False)
    archived_at = Column(DateTime, nullable=True)

    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<ChatSession(id={self.id}, user_id={self.user_id}, title={self.title!r})>"

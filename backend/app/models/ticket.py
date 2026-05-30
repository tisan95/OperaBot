"""Ticket model for incident escalation."""

from enum import Enum as PyEnum
from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base, GUID


class TicketStatus(str, PyEnum):
    """Ticket status enumeration."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class TicketPriority(str, PyEnum):
    """Ticket priority enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Ticket(Base):
    """Ticket model for issue escalation."""

    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(GUID(), ForeignKey("companies.id"), nullable=False, index=True)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    status = Column(
        Enum(
            TicketStatus,
            values_callable=lambda x: [e.value.lower() for e in x],
        ),
        default=TicketStatus.OPEN,
        nullable=False,
    )
    priority = Column(
        Enum(
            TicketPriority,
            values_callable=lambda x: [e.value.lower() for e in x],
        ),
        default=TicketPriority.MEDIUM,
        nullable=False,
    )
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    user = relationship("User")
    company = relationship("Company")

    def __repr__(self) -> str:
        return (
            f"<Ticket(id={self.id}, company_id={self.company_id}, user_id={self.user_id}, "
            f"status={self.status}, priority={self.priority})>"
        )
"""Ticket model for incident escalation."""

from enum import Enum as PyEnum
from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base, GUID


class TicketStatus(str, PyEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class TicketPriority(str, PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(GUID(), ForeignKey("companies.id"), nullable=False, index=True)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    status = Column(
        Enum(TicketStatus, values_callable=lambda x: [e.value.lower() for e in x]),
        default=TicketStatus.OPEN,
        nullable=False,
    )
    priority = Column(
        Enum(TicketPriority, values_callable=lambda x: [e.value.lower() for e in x]),
        default=TicketPriority.MEDIUM,
        nullable=False,
    )
    notes = Column(Text, nullable=True)
    resolution_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    user = relationship("User", foreign_keys=[user_id])
    company = relationship("Company")
    ticket_notes = relationship(
        "TicketNote",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="TicketNote.created_at",
    )

    def __repr__(self) -> str:
        return (
            f"<Ticket(id={self.id}, company_id={self.company_id}, "
            f"status={self.status}, priority={self.priority})>"
        )


class TicketNote(Base):
    """Internal note on a ticket, visible only to admins."""

    __tablename__ = "ticket_notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(
        Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    ticket = relationship("Ticket", back_populates="ticket_notes")
    author = relationship("User", foreign_keys=[author_id])

    def __repr__(self) -> str:
        return f"<TicketNote(id={self.id}, ticket_id={self.ticket_id})>"

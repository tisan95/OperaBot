"""Ticket API schemas."""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TicketCreateRequest(BaseModel):
    question: str = Field(..., min_length=1)
    priority: Optional[TicketPriority] = TicketPriority.MEDIUM


class TicketUpdateRequest(BaseModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    notes: Optional[str] = None
    resolution_message: Optional[str] = None


class TicketResponse(BaseModel):
    id: int
    question: str
    status: TicketStatus
    priority: TicketPriority
    notes: Optional[str] = None
    resolution_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    user_email: Optional[str] = None

    class Config:
        from_attributes = True


class TicketNoteCreate(BaseModel):
    content: str = Field(..., min_length=1)


class TicketNoteResponse(BaseModel):
    id: int
    ticket_id: int
    author_id: str
    author_email: Optional[str] = None
    content: str
    created_at: datetime

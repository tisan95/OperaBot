"""Ticket API schemas."""

from datetime import datetime
from enum import Enum
from typing import Optional
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


class TicketResponse(BaseModel):
    id: int
    question: str
    status: TicketStatus
    priority: TicketPriority
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True

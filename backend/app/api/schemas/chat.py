"""Chat request and response schemas."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1)


class ChatMessageResponse(BaseModel):
    id: int
    user_message: str
    bot_message: str
    sources: List[Dict[str, str]] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    created_at: datetime
    # ui_hint tells the frontend which action buttons to show.
    # "resolution_prompt" → [Sí, resuelto] [No, escalar]
    # "escalate_prompt"   → [Escalar] [No, gracias]
    # None                → no buttons
    ui_hint: Optional[str] = None

    class Config:
        from_attributes = True


class EscalateRequest(BaseModel):
    """Escalate the current conversation to a support ticket."""
    question: str = Field(..., min_length=1)


class EscalateResponse(BaseModel):
    ticket_id: int
    message: str = "Tu consulta ha sido escalada al equipo."

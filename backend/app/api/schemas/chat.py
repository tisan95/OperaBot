"""Chat request and response schemas."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    """Chat message request."""

    message: str = Field(..., min_length=1, description="User message text")


class ChatMessageResponse(BaseModel):
    """Chat message response with RAG sources."""

    id: int
    user_message: str
    bot_message: str
    sources: List[Dict[str, str]] = Field(default_factory=list, description="Sources used for answer")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score 0-1")
    created_at: datetime

    class Config:
        from_attributes = True


class ChatRatingRequest(BaseModel):
    """Chat rating request."""

    rating: int = Field(..., ge=1, le=5, description="Rating for the chat response")


class ChatRatingResponse(BaseModel):
    """Chat rating response."""

    id: int
    rating: int
    created_at: datetime

    class Config:
        from_attributes = True

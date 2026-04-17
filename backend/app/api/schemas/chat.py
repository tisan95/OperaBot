"""Chat request and response schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    """Chat message request."""

    message: str = Field(..., min_length=1, description="User message text")


class ChatMessageResponse(BaseModel):
    """Chat message response."""

    id: int
    user_message: str
    bot_message: str
    is_fallback: bool
    rating: Optional[int] = None
    created_at: datetime

    class Config:
        orm_mode = True


class ChatRatingRequest(BaseModel):
    """Chat rating request."""

    rating: int = Field(..., ge=1, le=5, description="Rating for the chat response")


class ChatRatingResponse(BaseModel):
    """Chat rating response."""

    id: int
    rating: int
    created_at: datetime

    class Config:
        orm_mode = True

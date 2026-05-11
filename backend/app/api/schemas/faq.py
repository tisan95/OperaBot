"""FAQ request and response schemas."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class FAQBase(BaseModel):
    """Base FAQ payload."""

    question: str = Field(..., min_length=1, description="FAQ question")
    answer: str = Field(..., min_length=1, description="FAQ answer")
    category: Optional[str] = Field(None, max_length=255, description="FAQ category")


class FAQCreate(FAQBase):
    """FAQ create payload."""


class FAQRead(FAQBase):
    """FAQ read payload."""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True

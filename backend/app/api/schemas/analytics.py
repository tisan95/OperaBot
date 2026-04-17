"""Analytics response schemas."""

from typing import List
from pydantic import BaseModel


class TopQuestionItem(BaseModel):
    """Top question item for analytics."""

    question: str
    count: int


class AnalyticsResponse(BaseModel):
    """Aggregated analytics response."""

    total_chats_today: int
    success_rate: float
    top_questions: List[TopQuestionItem]

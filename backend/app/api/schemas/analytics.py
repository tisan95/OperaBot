"""Analytics response schemas."""

from typing import List, Optional
from pydantic import BaseModel


class TopQuestionItem(BaseModel):
    """Top question item for analytics."""

    question: str
    count: int


class ServiceHealthStatus(BaseModel):
    """Service health status."""

    service: str
    status: str  # "healthy" | "unavailable"
    message: str = ""


class DocumentStatsItem(BaseModel):
    """Document statistics."""

    total_documents: int
    total_vectors: int
    total_size_bytes: int
    documents_processed_today: int


class FAQStatsItem(BaseModel):
    """FAQ statistics."""

    total_faqs: int
    total_vectors: int
    last_updated: Optional[str] = None


class ChatStatsItem(BaseModel):
    """Chat statistics for today."""

    total_chats_today: int
    success_rate: float
    avg_response_time_ms: float = 0.0
    avg_confidence: float = 0.0


class PerformanceMetrics(BaseModel):
    """Performance metrics."""

    avg_response_time_ms: float
    avg_confidence: float
    vectors_created_today: int
    docs_processed_today: int


class AnalyticsResponse(BaseModel):
    """Aggregated analytics response."""

    total_chats_today: int
    success_rate: float
    top_questions: List[TopQuestionItem]


class SystemStatsResponse(BaseModel):
    """Complete system statistics for dashboard."""

    documents: DocumentStatsItem
    faqs: FAQStatsItem
    chat_today: ChatStatsItem
    services: List[ServiceHealthStatus]
    performance: PerformanceMetrics
    timestamp: str  # ISO format datetime

"""Admin analytics API routes."""

from datetime import datetime
from typing import List
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user_id, get_current_company_id
from app.api.schemas.analytics import (
    AnalyticsResponse,
    TopQuestionItem,
    SystemStatsResponse,
    ServiceHealthStatus,
    DocumentStatsItem,
    FAQStatsItem,
    ChatStatsItem,
    PerformanceMetrics,
)
from app.db.database import get_db
from app.models.chat_message import ChatMessage
from app.models.user import User, UserRole
from app.models.document import Document
from app.models.faq import FAQ
from app.config import settings

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
) -> AnalyticsResponse:
    """Return analytics data for the current company."""
    result = await db.execute(
        select(User).where(User.id == user_id, User.company_id == company_id)
    )
    user = result.scalar_one_or_none()
    if not user or user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    chat_filter = (
        ChatMessage.company_id == company_id,
        ChatMessage.created_at >= today_start,
    )

    total_chats = await db.scalar(
        select(func.count())
        .select_from(ChatMessage)
        .where(*chat_filter)
    )

    successful_chats = await db.scalar(
        select(func.count())
        .select_from(ChatMessage)
        .where(*chat_filter, ChatMessage.is_fallback == False)
    )

    top_questions_result = await db.execute(
        select(
            ChatMessage.user_message,
            func.count(ChatMessage.id).label("count"),
        )
        .where(*chat_filter)
        .group_by(ChatMessage.user_message)
        .order_by(desc("count"))
        .limit(3)
    )

    top_questions: List[TopQuestionItem] = [
        TopQuestionItem(question=row[0], count=row[1])
        for row in top_questions_result.all()
    ]

    success_rate = 0.0
    if total_chats and total_chats > 0:
        success_rate = float(successful_chats or 0) / float(total_chats)

    return AnalyticsResponse(
        total_chats_today=int(total_chats or 0),
        success_rate=success_rate,
        top_questions=top_questions,
    )


async def _check_qdrant_health() -> ServiceHealthStatus:
    """Check Qdrant health status real."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # FIX: La ruta correcta para hacer ping a Qdrant es la raíz /
            response = await client.get("http://localhost:6333/")
            if response.status_code == 200:
                return ServiceHealthStatus(
                    service="Qdrant",
                    status="healthy",
                    message="Vector database ready"
                )
    except Exception as e:
        pass
    
    return ServiceHealthStatus(
        service="Qdrant",
        status="unavailable",
        message="Vector database unreachable"
    )


async def _check_ollama_health() -> ServiceHealthStatus:
    """Check Ollama health status real."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                
                # FIX: Sacar los nombres reales de los modelos (ej. llama3.2, nomic-embed-text)
                # Limpiamos el ":latest" para que quede más elegante visualmente
                model_names = [m.get("name", "").replace(":latest", "") for m in models][:3]
                
                if model_names:
                    models_str = " & ".join(model_names)
                    if len(models) > 3:
                        models_str += f" (+{len(models)-3} more)"
                else:
                    models_str = "No models loaded"

                return ServiceHealthStatus(
                    service="Ollama Local AI",
                    status="healthy",
                    message=models_str
                )
    except Exception as e:
        pass
    
    return ServiceHealthStatus(
        service="Ollama Local AI",
        status="unavailable",
        message="LLM service unreachable"
    )


async def _check_postgres_health(db: AsyncSession) -> ServiceHealthStatus:
    """Check PostgreSQL health status real."""
    try:
        await db.scalar(select(func.count()).select_from(User))
        return ServiceHealthStatus(
            service="PostgreSQL",
            status="healthy",
            message="Database connected"
        )
    except Exception as e:
        return ServiceHealthStatus(
            service="PostgreSQL",
            status="unavailable",
            message="Database connection failed"
        )


@router.get("/system-stats", response_model=SystemStatsResponse)
async def get_system_stats(
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
) -> SystemStatsResponse:
    """Return system statistics for dashboard (admin only)."""
    # Verify admin role
    result = await db.execute(
        select(User).where(User.id == user_id, User.company_id == company_id)
    )
    user = result.scalar_one_or_none()
    if not user or user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    # Document statistics
    doc_count = await db.scalar(
        select(func.count())
        .select_from(Document)
        .where(Document.company_id == company_id)
    )
    doc_vectors = await db.scalar(
        select(func.sum(Document.vector_count))
        .select_from(Document)
        .where(Document.company_id == company_id)
    )
    doc_size = await db.scalar(
        select(func.sum(Document.file_size))
        .select_from(Document)
        .where(Document.company_id == company_id)
    )

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    docs_today = await db.scalar(
        select(func.count())
        .select_from(Document)
        .where(
            Document.company_id == company_id,
            Document.created_at >= today_start,
            Document.upload_status == "completed"
        )
    )

    # FAQ statistics
    faq_count = await db.scalar(
        select(func.count())
        .select_from(FAQ)
        .where(FAQ.company_id == company_id)
    )
    faq_vectors = faq_count * 1 if faq_count else 0  # Simplified: 1 vector per FAQ

    faq_last_updated = await db.scalar(
        select(FAQ.created_at)
        .where(FAQ.company_id == company_id)
        .order_by(desc(FAQ.created_at))
        .limit(1)
    )

    # Chat statistics (today)
    chat_filter = (
        ChatMessage.company_id == company_id,
        ChatMessage.created_at >= today_start,
    )

    total_chats = await db.scalar(
        select(func.count())
        .select_from(ChatMessage)
        .where(*chat_filter)
    ) or 0

    successful_chats = await db.scalar(
        select(func.count())
        .select_from(ChatMessage)
        .where(*chat_filter, ChatMessage.is_fallback == False)
    ) or 0

    success_rate = 0.0
    if total_chats > 0:
        success_rate = float(successful_chats) / float(total_chats)

    # Performance metrics
    avg_response_ms = 0.0
    avg_confidence = 0.0

    if total_chats > 0:
        # Query average confidence from chat messages
        avg_confidence_result = await db.scalar(
            select(func.avg(ChatMessage.confidence))
            .where(*chat_filter)
        )
        avg_confidence = float(avg_confidence_result or 0.0)

    # Health checks (parallel)
    qdrant_health = await _check_qdrant_health()
    ollama_health = await _check_ollama_health()
    postgres_health = await _check_postgres_health(db)

    services = [qdrant_health, ollama_health, postgres_health]

    documents_stats = DocumentStatsItem(
        total_documents=int(doc_count or 0),
        total_vectors=int(doc_vectors or 0),
        total_size_bytes=int(doc_size or 0),
        documents_processed_today=int(docs_today or 0),
    )

    faqs_stats = FAQStatsItem(
        total_faqs=int(faq_count or 0),
        total_vectors=int(faq_vectors),
        last_updated=faq_last_updated.isoformat() if faq_last_updated else None,
    )

    chat_stats = ChatStatsItem(
        total_chats_today=int(total_chats),
        success_rate=success_rate,
        avg_response_time_ms=avg_response_ms,
        avg_confidence=avg_confidence,
    )

    performance = PerformanceMetrics(
        avg_response_time_ms=avg_response_ms,
        avg_confidence=avg_confidence,
        vectors_created_today=int(docs_today or 0),
        docs_processed_today=int(docs_today or 0),
    )

    return SystemStatsResponse(
        documents=documents_stats,
        faqs=faqs_stats,
        chat_today=chat_stats,
        services=services,
        performance=performance,
        timestamp=datetime.utcnow().isoformat(),
    )
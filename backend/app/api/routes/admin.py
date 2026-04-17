"""Admin analytics API routes."""

from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user_id, get_current_company_id
from app.api.schemas.analytics import AnalyticsResponse, TopQuestionItem
from app.db.database import get_db
from app.models.chat_message import ChatMessage
from app.models.user import User, UserRole

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

"""Chat endpoint with RAG (Retrieval Augmented Generation)."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List, Dict, Any

from app.api.dependencies import get_current_company_id, get_current_user_id
from app.api.schemas.chat import ChatMessageRequest, ChatMessageResponse
from app.db.database import get_db
from app.models.chat_message import ChatMessage
from app.services.llm_client import generate_answer_with_sources

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


async def _save_chat_message(
    db: AsyncSession,
    company_id: str,
    user_id: str,
    user_message: str,
    bot_response: Dict[str, Any],
) -> ChatMessage:
    """Save chat message with sources and confidence to database."""
    chat_entry = ChatMessage(
        company_id=company_id,
        user_id=user_id,
        user_message=user_message,
        bot_message=bot_response.get("answer", ""),
        confidence=bot_response.get("confidence", 0.0),
        is_fallback=False,  # RAG responses are not fallback
    )
    db.add(chat_entry)
    await db.commit()
    await db.refresh(chat_entry)
    return chat_entry


@router.post("/messages", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
async def chat_message(
    request: ChatMessageRequest,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
) -> ChatMessageResponse:
    """Send a chat message and receive an AI-generated response with sources."""
    logger.info(f"POST /chat/messages - User {user_id}, Message: '{request.message[:50]}...'")

    user_message = request.message.strip()
    if not user_message:
        logger.warning(f"User {user_id} sent empty message")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please enter a message to continue.",
        )

    try:
        # Generate answer with RAG (searches FAQs + Documents)
        logger.info(f"Generating RAG answer for company {company_id}")
        bot_response = await generate_answer_with_sources(user_message, company_id)
        
        # Save chat message
        chat_entry = await _save_chat_message(
            db=db,
            company_id=company_id,
            user_id=user_id,
            user_message=user_message,
            bot_response=bot_response,
        )

        logger.info(f"Chat saved: {chat_entry.id}, sources: {len(bot_response.get('sources', []))}")

        return ChatMessageResponse(
            id=chat_entry.id,
            user_message=user_message,
            bot_message=bot_response.get("answer", ""),
            sources=bot_response.get("sources", []),
            confidence=bot_response.get("confidence", 0.0),
            created_at=chat_entry.created_at,
        )

    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        try:
            await db.rollback()
        except Exception:
            pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing your message. Please try again.",
        )


@router.get("/history", response_model=List[ChatMessageResponse])
async def get_chat_history(
    limit: int = 50,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
) -> List[ChatMessageResponse]:
    """Get chat history for the current user."""
    try:
        result = await db.execute(
            select(ChatMessage)
            .where(
                (ChatMessage.company_id == company_id) & 
                (ChatMessage.user_id == user_id)
            )
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        messages = list(result.scalars().all())
        
        # Reverse to show oldest first
        messages.reverse()
        
        return [
            ChatMessageResponse(
                id=msg.id,
                user_message=msg.user_message,
                bot_message=msg.bot_message,
                sources=[],  # History doesn't include sources for now
                confidence=0.0,
                created_at=msg.created_at,
            )
            for msg in messages
        ]
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching chat history.",
        )

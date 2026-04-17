import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.api.dependencies import get_current_company_id, get_current_user_id
from app.api.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatRatingRequest,
    ChatRatingResponse,
)
from app.db.database import get_db
from app.models.chat_message import ChatMessage
from app.models.faq import FAQ
from app.services.llm_client import generate_answer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


def _is_fallback_response(bot_message: str) -> bool:
    return bot_message.startswith("Thanks for your message:")


async def _save_chat_message(
    db: AsyncSession,
    company_id: str,
    user_id: str,
    user_message: str,
    bot_message: str,
    is_fallback: bool,
) -> ChatMessage:
    chat_entry = ChatMessage(
        company_id=company_id,
        user_id=user_id,
        user_message=user_message,
        bot_message=bot_message,
        is_fallback=is_fallback,
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
    """Send a chat message and receive an AI-generated response."""
    logger.info(f"📬 POST /chat/messages - User {user_id}, Message: '{request.message[:50]}...'")

    user_message = request.message.strip()
    if not user_message:
        logger.warning(f"User {user_id} sent empty message")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please enter a message to continue.",
        )

    faqs = []
    try:
        result = await db.execute(
            select(FAQ)
            .where(FAQ.company_id == company_id)
            .order_by(FAQ.created_at.desc())
        )
        faqs = list(result.scalars().all())
        logger.info(f"✅ Loaded {len(faqs)} FAQs from database for company {company_id}")
    except Exception as faq_err:
        logger.warning(
            f"Failed to fetch FAQ context: {type(faq_err).__name__}: {faq_err}"
        )

    try:
        logger.info(f"🤖 Calling generate_answer() with {len(faqs)} FAQs as context...")
        bot_message = await generate_answer(user_message, faqs)
        logger.info(f"✅ Got response from LLM/fallback: {len(bot_message)} chars")
    except Exception as llm_err:
        logger.error(
            f"❌ Unexpected error in generate_answer: {type(llm_err).__name__}: {llm_err}",
            exc_info=True,
        )
        bot_message = f"Thanks for your message: '{user_message}'. I'm learning to respond better!"
        # Rollback any pending transaction to avoid InFailedSQLTransactionError
        try:
            await db.rollback()
            logger.info("✅ Database transaction rolled back")
        except Exception as rollback_err:
            logger.warning(f"Failed to rollback transaction: {rollback_err}")

    is_fallback = _is_fallback_response(bot_message)
    try:
        chat_entry = await _save_chat_message(
            db,
            company_id=company_id,
            user_id=user_id,
            user_message=user_message,
            bot_message=bot_message,
            is_fallback=is_fallback,
        )
    except Exception as db_err:
        logger.error(
            f"❌ Failed to save chat history: {type(db_err).__name__}: {db_err}",
            exc_info=True,
        )
        # Rollback to clean up any failed transaction
        try:
            await db.rollback()
            logger.info("✅ Database transaction rolled back after save failure")
        except Exception as rollback_err:
            logger.warning(f"Failed to rollback transaction: {rollback_err}")
        
        return ChatMessageResponse(
            id=-1,
            user_message=user_message,
            bot_message=bot_message,
            is_fallback=is_fallback,
            rating=None,
            created_at=datetime.utcnow(),
        )

    logger.info(f"📤 Returning chat response to user {user_id}")
    return ChatMessageResponse(
        id=chat_entry.id,
        user_message=chat_entry.user_message,
        bot_message=chat_entry.bot_message,
        is_fallback=chat_entry.is_fallback,
        rating=chat_entry.rating,
        created_at=chat_entry.created_at,
    )


@router.put(
    "/messages/{chat_id}/rating",
    response_model=ChatRatingResponse,
    status_code=status.HTTP_200_OK,
)
async def rate_chat_message(
    chat_id: int,
    request: ChatRatingRequest,
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
) -> ChatRatingResponse:
    """Save a basic rating for a chat conversation."""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.id == chat_id)
        .where(ChatMessage.company_id == company_id)
    )
    chat_entry = result.scalar_one_or_none()
    if not chat_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat message not found.",
        )

    chat_entry.rating = request.rating
    await db.commit()
    await db.refresh(chat_entry)

    return ChatRatingResponse(
        id=chat_entry.id,
        rating=chat_entry.rating,
        created_at=chat_entry.updated_at or chat_entry.created_at,
    )

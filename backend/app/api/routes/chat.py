import logging
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.api.dependencies import get_current_user_id
from app.db.database import get_db
from app.models.faq import FAQ
from app.services.llm_client import generate_answer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessageRequest(BaseModel):
    """Chat message request."""

    message: str = Field(..., min_length=1, description="User message text")


class ChatMessageResponse(BaseModel):
    """Chat message response."""

    id: str
    user_message: str
    bot_message: str
    created_at: datetime


@router.post("/messages", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
async def chat_message(
    request: ChatMessageRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ChatMessageResponse:
    """Send a chat message and receive an AI-generated response.

    Fetches FAQ context and uses the configured LLM provider to generate an answer.
    Falls back to a placeholder response if LLM is not configured or if any error occurs.

    This endpoint is designed to always succeed. Even if the LLM API fails, FAQ
    fetch fails, or any other error occurs, it will return a graceful fallback response.
    """
    logger.info(f"📬 POST /chat/messages - User {user_id}, Message: '{request.message[:50]}...'")
    
    try:
        # Validate and clean user input
        user_message = request.message.strip()
        if not user_message:
            logger.warning(f"User {user_id} sent empty message")
            return ChatMessageResponse(
                id="1",
                user_message=user_message,
                bot_message="Please enter a message to continue.",
                created_at=datetime.utcnow(),
            )

        # Attempt to fetch FAQ context (non-critical, proceed without if it fails)
        faqs = []
        try:
            result = await db.execute(select(FAQ).order_by(FAQ.created_at.desc()))
            faqs = list(result.scalars().all())
            logger.info(f"✅ Loaded {len(faqs)} FAQs from database")
        except Exception as faq_err:
            logger.warning(f"Failed to fetch FAQ context: {type(faq_err).__name__}: {faq_err}")
            # Continue without FAQ context - LLM will still respond

        # Generate answer using LLM (with FAQ context, falls back to placeholder if needed)
        try:
            logger.info(f"🤖 Calling generate_answer() with {len(faqs)} FAQs as context...")
            bot_message = await generate_answer(user_message, faqs)
            logger.info(f"✅ Got response from LLM/fallback: {len(bot_message)} chars")
            
            # Log if we got a fallback response (heuristic: check if it's the generic fallback)
            if "I'm learning to respond better" in bot_message:
                logger.warning("⚠️ Response appears to be a fallback message (generic text detected)")
            else:
                logger.info("✅ Response appears to be from Gemini API (not generic fallback)")
                
        except Exception as llm_err:
            logger.error(f"❌ Unexpected error in generate_answer: {type(llm_err).__name__}: {llm_err}", exc_info=True)
            bot_message = f"Thanks for your message: '{user_message}'. I'm learning to respond better!"

        # Return response (stateless, not persisted)
        logger.info(f"📤 Returning chat response to user {user_id}")
        return ChatMessageResponse(
            id="1",
            user_message=user_message,
            bot_message=bot_message,
            created_at=datetime.utcnow(),
        )

    except Exception as e:
        # Final safety net: if anything unexpected happens, return a safe response
        logger.error(f"❌ Unexpected error in chat_message endpoint: {type(e).__name__}: {e}", exc_info=True)
        fallback_message = "Thanks for your message. I'm having trouble responding right now, but your message was received."
        return ChatMessageResponse(
            id="1",
            user_message=request.message.strip() or "[empty]",
            bot_message=fallback_message,
            created_at=datetime.utcnow(),
        )

"""Chat endpoint with intent classification + RAG."""

import logging
from datetime import datetime
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_company_id, get_current_user_id
from app.api.limiter import limiter
from app.api.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    EscalateRequest,
    EscalateResponse,
)
from app.db.database import get_db
from app.models.chat_message import ChatMessage
from app.models.ticket import Ticket, TicketPriority
from app.services.llm_client import (
    classify_intent,
    generate_answer_with_sources,
    greeting_response,
    confirmation_response,
    negation_response,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


async def _save_chat(
    db: AsyncSession,
    company_id: str,
    user_id: str,
    user_message: str,
    bot_response: Dict[str, Any],
) -> ChatMessage:
    entry = ChatMessage(
        company_id=company_id,
        user_id=user_id,
        user_message=user_message,
        bot_message=bot_response["answer"],
        sources=bot_response.get("sources", []),
        confidence=bot_response.get("confidence", 0.0),
        is_fallback=False,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


async def _count_recent_rag_exchanges(
    db: AsyncSession, user_id: str, company_id: str
) -> int:
    """Count consecutive recent messages with RAG answers (confidence > 0)."""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == user_id, ChatMessage.company_id == company_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(5)
    )
    count = 0
    for msg in result.scalars().all():
        if (msg.confidence or 0.0) > 0:
            count += 1
        else:
            break
    return count


# ── POST /chat/messages ──────────────────────────────────────────────────────

@router.post("/messages", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def chat_message(
    request: Request,
    body: ChatMessageRequest,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
) -> ChatMessageResponse:
    user_message = body.message.strip()
    if not user_message:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El mensaje no puede estar vacío.")

    intent = classify_intent(user_message)
    logger.info(f"[chat] user={user_id} intent={intent} msg='{user_message[:60]}'")

    try:
        if intent == "GREETING":
            bot_response = greeting_response()

        elif intent == "CONFIRMATION":
            bot_response = confirmation_response()

        elif intent == "NEGATION":
            bot_response = negation_response()

        else:  # QUESTION
            recent_rag = await _count_recent_rag_exchanges(db, user_id, company_id)
            bot_response = await generate_answer_with_sources(
                user_message, company_id, recent_rag_count=recent_rag
            )

        entry = await _save_chat(db, company_id, user_id, user_message, bot_response)
        logger.info(f"[chat] saved message id={entry.id} confidence={bot_response.get('confidence', 0):.2f}")

        return ChatMessageResponse(
            id=entry.id,
            user_message=user_message,
            bot_message=bot_response["answer"],
            sources=bot_response.get("sources", []),
            confidence=bot_response.get("confidence", 0.0),
            created_at=entry.created_at,
            ui_hint=bot_response.get("ui_hint"),
        )

    except Exception as e:
        logger.error(f"[chat] Error: {e}", exc_info=True)
        try:
            await db.rollback()
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error procesando tu mensaje. Por favor, intenta de nuevo.",
        )


# ── POST /chat/escalate ──────────────────────────────────────────────────────

@router.post("/escalate", response_model=EscalateResponse, status_code=status.HTTP_201_CREATED)
async def escalate_chat(
    body: EscalateRequest,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
) -> EscalateResponse:
    """Create a support ticket with the last conversation messages as context."""
    # Get last 5 messages to build context
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == user_id, ChatMessage.company_id == company_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(5)
    )
    recent = list(reversed(result.scalars().all()))

    context_lines = []
    for msg in recent:
        context_lines.append(f"Usuario: {msg.user_message}")
        bot_preview = (msg.bot_message or "")[:300]
        context_lines.append(f"Bot: {bot_preview}{'...' if len(msg.bot_message or '') > 300 else ''}")
    context = "\n".join(context_lines)

    ticket = Ticket(
        company_id=company_id,
        user_id=user_id,
        question=body.question,
        priority=TicketPriority.MEDIUM,
        notes=f"Contexto de la conversación:\n{context}" if context else None,
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)

    logger.info(f"[chat] Ticket #{ticket.id} creado por escalado manual, user={user_id}")

    return EscalateResponse(
        ticket_id=ticket.id,
        message=f"Tu consulta ha sido escalada. Ticket #{ticket.id} creado — el equipo lo revisará pronto.",
    )


# ── GET /chat/history ────────────────────────────────────────────────────────

@router.get("/history", response_model=List[ChatMessageResponse])
async def get_chat_history(
    limit: int = 50,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
) -> List[ChatMessageResponse]:
    try:
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.company_id == company_id, ChatMessage.user_id == user_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        messages = list(reversed(result.scalars().all()))
        return [
            ChatMessageResponse(
                id=msg.id,
                user_message=msg.user_message,
                bot_message=msg.bot_message,
                sources=msg.sources or [],
                confidence=msg.confidence or 0.0,
                created_at=msg.created_at,
                ui_hint=None,  # history messages don't show action buttons
            )
            for msg in messages
        ]
    except Exception as e:
        logger.error(f"[chat] Error fetching history: {e}")
        raise HTTPException(status_code=500, detail="Error obteniendo el historial.")

"""Inbound webhooks from third-party systems.

FreeScout: when an agent replies to a conversation from the real mailbox
(not from OperaBot), that reply is mirrored back onto the linked ticket so
the customer sees it in /my-tickets without the admin having to duplicate
the work in OperaBot.

Every request is authenticated via HMAC signature (see freescout_service.
verify_webhook_signature) rather than a session cookie — the caller is an
external server, not a logged-in user.
"""

import json
import logging
from datetime import datetime

from fastapi import APIRouter, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.db.database import get_db
from app.models.ticket import Ticket, TicketStatus
from app.services import freescout_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# Confirmed from FreeScout's public docs; payload field names inside each
# event are NOT publicly documented — see the note at the top of
# freescout_service.py before touching the parsing logic below.
_AGENT_REPLY_EVENT = "convo.agent.reply.created"


@router.post("/freescout", status_code=200)
async def freescout_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Response:
    raw_body = await request.body()
    signature = request.headers.get("X-FreeScout-Signature")

    if not freescout_service.verify_webhook_signature(raw_body, signature):
        logger.warning("[freescout webhook] Firma inválida o ausente — request rechazada.")
        return Response(status_code=401)

    try:
        payload = json.loads(raw_body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        logger.error(f"[freescout webhook] Body no es JSON válido: {raw_body[:300]!r}")
        return Response(status_code=200)  # ack anyway — retrying won't fix a malformed body

    event = payload.get("event") or payload.get("eventType") or payload.get("type")
    logger.info(f"[freescout webhook] Recibido evento={event!r}")

    if event != _AGENT_REPLY_EVENT:
        # convo.status, convo.created, etc. — not handled yet, just acknowledged.
        return Response(status_code=200)

    conversation_id = freescout_service.extract_conversation_id(payload)
    reply_text = freescout_service.extract_reply_text(payload)
    if conversation_id is None or reply_text is None:
        logger.error("[freescout webhook] No se pudo extraer conversationId/texto — ver payload arriba.")
        return Response(status_code=200)

    result = await db.execute(
        select(Ticket).where(Ticket.freescout_conversation_id == conversation_id)
    )
    ticket = result.scalar_one_or_none()
    if not ticket:
        logger.warning(f"[freescout webhook] Ningún ticket vinculado a conversation #{conversation_id}")
        return Response(status_code=200)

    ticket.resolution_message = reply_text
    if ticket.status != TicketStatus.RESOLVED:
        ticket.status = TicketStatus.RESOLVED
        ticket.resolved_at = datetime.utcnow()
    ticket.updated_at = datetime.utcnow()
    await db.commit()

    logger.info(f"[freescout webhook] Ticket #{ticket.id} actualizado desde conversation #{conversation_id}")
    return Response(status_code=200)

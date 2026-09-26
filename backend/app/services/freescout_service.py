"""FreeScout mailbox sync — one-way outbound (create/reply) + inbound webhook verification.

Requires the paid "API & Webhooks" module on the customer's FreeScout instance.
Disabled by default (FREESCOUT_ENABLED=false) so a missing/misconfigured instance
never blocks the local ticket flow — every call here is best-effort and swallows
its own errors.

NOTE on inbound webhook payload shape: FreeScout's public docs confirm the event
names (convo.agent.reply.created, convo.status, ...) and the signature scheme,
but do not document the exact JSON field names for the payload body. The parser
below tries the field names used by FreeScout's own API resources elsewhere
(conversationId / conversation.id, text / thread.text) and logs the raw payload
whenever it can't find them — treat that log line as the fix location once a
real instance is wired up and sends its first webhook.
"""

import base64
import hashlib
import hmac
import logging
from typing import Any, Dict, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def is_enabled() -> bool:
    return bool(
        settings.FREESCOUT_ENABLED
        and settings.FREESCOUT_BASE_URL
        and settings.FREESCOUT_API_KEY
        and settings.FREESCOUT_MAILBOX_ID
    )


def _headers() -> Dict[str, str]:
    return {
        "X-FreeScout-API-Key": settings.FREESCOUT_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


async def create_conversation(subject: str, customer_email: str, body_text: str) -> Optional[int]:
    """Create a FreeScout conversation for a newly escalated ticket.

    Returns the FreeScout conversation id, or None if disabled/unreachable
    (never raises — a down mailbox must not block ticket creation).
    """
    if not is_enabled():
        return None

    url = f"{settings.FREESCOUT_BASE_URL.rstrip('/')}/api/conversations"
    payload = {
        "type": "email",
        "mailboxId": settings.FREESCOUT_MAILBOX_ID,
        "subject": subject[:255],
        "customer": {"email": customer_email},
        "threads": [{
            "type": "customer",
            "text": body_text,
            "customer": {"email": customer_email},
        }],
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload, headers=_headers())
        if resp.status_code not in (200, 201):
            logger.error(f"[freescout] create_conversation {resp.status_code}: {resp.text[:300]}")
            return None
        conversation_id = resp.headers.get("Resource-ID")
        if conversation_id:
            return int(conversation_id)
        data = resp.json() if resp.content else {}
        return data.get("id")
    except Exception as e:
        logger.error(f"[freescout] create_conversation failed: {type(e).__name__}: {e}")
        return None


async def add_agent_reply(conversation_id: int, text: str) -> bool:
    """Post the admin's resolution as an agent reply on an existing conversation."""
    if not is_enabled():
        return False
    if not settings.FREESCOUT_AGENT_USER_ID:
        logger.warning(
            "[freescout] FREESCOUT_AGENT_USER_ID no configurado — no se puede "
            "atribuir la respuesta a un agente, se omite el envío."
        )
        return False

    url = f"{settings.FREESCOUT_BASE_URL.rstrip('/')}/api/conversations/{conversation_id}/threads"
    payload = {
        "type": "message",
        "text": text,
        "user": settings.FREESCOUT_AGENT_USER_ID,
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload, headers=_headers())
        if resp.status_code not in (200, 201):
            logger.error(f"[freescout] add_agent_reply {resp.status_code}: {resp.text[:300]}")
            return False
        return True
    except Exception as e:
        logger.error(f"[freescout] add_agent_reply failed: {type(e).__name__}: {e}")
        return False


def verify_webhook_signature(raw_body: bytes, signature_header: Optional[str]) -> bool:
    """Verify X-FreeScout-Signature: base64(HMAC-SHA1(raw_body, webhook_secret))."""
    if not settings.FREESCOUT_WEBHOOK_SECRET or not signature_header:
        return False
    computed = base64.b64encode(
        hmac.new(
            settings.FREESCOUT_WEBHOOK_SECRET.encode("utf-8"),
            raw_body,
            hashlib.sha1,
        ).digest()
    ).decode("utf-8")
    return hmac.compare_digest(computed, signature_header)


def extract_conversation_id(payload: Dict[str, Any]) -> Optional[int]:
    """Best-effort extraction across the plausible FreeScout payload shapes."""
    for path in (
        ("conversationId",),
        ("id",),
        ("conversation", "id"),
    ):
        node: Any = payload
        for key in path:
            if not isinstance(node, dict) or key not in node:
                node = None
                break
            node = node[key]
        if isinstance(node, int):
            return node
    logger.warning(f"[freescout] webhook: no se encontró conversationId en payload: {payload}")
    return None


def extract_reply_text(payload: Dict[str, Any]) -> Optional[str]:
    """Best-effort extraction of the agent reply body across plausible shapes."""
    if isinstance(payload.get("text"), str):
        return payload["text"]
    thread = payload.get("thread")
    if isinstance(thread, dict) and isinstance(thread.get("text"), str):
        return thread["text"]
    threads = payload.get("threads")
    if isinstance(threads, list) and threads and isinstance(threads[-1], dict):
        text = threads[-1].get("text")
        if isinstance(text, str):
            return text
    logger.warning(f"[freescout] webhook: no se encontró texto de respuesta en payload: {payload}")
    return None

"""Transactional email — provider dispatcher, same pattern as llm_client.py.

EMAIL_PROVIDER switches between:
  - mailhog: local SMTP capture for development (default, no external calls)
  - resend:  production HTTP API (inactive until EMAIL_PROVIDER=resend)

Every public function here is best-effort: it logs and returns False on any
failure instead of raising, because a broken mail provider must never break
the user-approval or ticket-resolution flow that triggered the email.
"""

import asyncio
import html as html_lib
import logging
import smtplib
from email.message import EmailMessage
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


# ── Dispatcher ────────────────────────────────────────────────────────────────

async def send_email(to_email: str, subject: str, html_body: str, text_body: str) -> bool:
    """Send an email via the configured provider. Never raises."""
    try:
        provider = (settings.EMAIL_PROVIDER or "mailhog").lower()
        if provider == "resend":
            return await _send_via_resend(to_email, subject, html_body, text_body)
        if provider != "mailhog":
            logger.warning(f"[email] Proveedor desconocido '{provider}', usando mailhog.")
        return await _send_via_mailhog(to_email, subject, html_body, text_body)
    except Exception as e:
        logger.error(f"[email] Error inesperado enviando a {to_email}: {type(e).__name__}: {e}", exc_info=True)
        return False


# ── MailHog (dev) ─────────────────────────────────────────────────────────────

def _build_message(to_email: str, subject: str, html_body: str, text_body: str) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM_ADDRESS
    msg["To"] = to_email
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")
    return msg


async def _send_via_mailhog(to_email: str, subject: str, html_body: str, text_body: str) -> bool:
    msg = _build_message(to_email, subject, html_body, text_body)

    def _sync_send():
        with smtplib.SMTP(settings.MAILHOG_HOST, settings.MAILHOG_PORT, timeout=5) as smtp:
            smtp.send_message(msg)

    try:
        await asyncio.to_thread(_sync_send)
        return True
    except Exception as e:
        logger.error(f"[email/mailhog] No se pudo enviar a {to_email}: {type(e).__name__}: {e}")
        return False


# ── Resend (production) ──────────────────────────────────────────────────────

async def _send_via_resend(to_email: str, subject: str, html_body: str, text_body: str) -> bool:
    if not settings.RESEND_API_KEY:
        logger.warning("[email/resend] RESEND_API_KEY no configurada — envío omitido.")
        return False

    url = "https://api.resend.com/emails"
    payload = {
        "from": settings.RESEND_FROM_EMAIL or settings.EMAIL_FROM_ADDRESS,
        "to": [to_email],
        "subject": subject,
        "html": html_body,
        "text": text_body,
    }
    headers = {"Authorization": f"Bearer {settings.RESEND_API_KEY}"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code not in (200, 201):
            logger.error(f"[email/resend] {resp.status_code}: {resp.text[:300]}")
            return False
        return True
    except httpx.TimeoutException:
        logger.error("[email/resend] Timeout llamando a la API de Resend.")
        return False
    except Exception as e:
        logger.error(f"[email/resend] Error: {type(e).__name__}: {e}")
        return False


# ── Templates ─────────────────────────────────────────────────────────────────

def _render_template(heading: str, message_html: str, cta_label: str, cta_url: str) -> str:
    """Simple inline-styled HTML matching the product's black/gold theme.

    Inline styles only — most email clients strip <style> blocks and all
    external stylesheets, so Tailwind classes don't survive the trip.
    """
    return f"""<!DOCTYPE html>
<html>
  <body style="margin:0;padding:0;background-color:#0A0A0A;font-family:Arial,Helvetica,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#0A0A0A;padding:32px 16px;">
      <tr>
        <td align="center">
          <table role="presentation" width="480" cellpadding="0" cellspacing="0" style="max-width:480px;width:100%;background-color:#111111;border:1px solid #2A2A2A;border-radius:12px;overflow:hidden;">
            <tr>
              <td style="padding:20px 32px;border-bottom:1px solid #2A2A2A;">
                <span style="color:#C9A84C;font-size:18px;font-weight:bold;letter-spacing:-0.02em;">OperaBot</span>
              </td>
            </tr>
            <tr>
              <td style="padding:32px;">
                <h1 style="color:#F5F5F5;font-size:17px;margin:0 0 16px;font-weight:600;">{heading}</h1>
                <p style="color:#AAAAAA;font-size:14px;line-height:1.6;margin:0 0 24px;">{message_html}</p>
                <a href="{cta_url}" style="display:inline-block;background-color:#C9A84C;color:#0A0A0A;text-decoration:none;padding:10px 22px;border-radius:8px;font-size:13px;font-weight:600;">{cta_label}</a>
              </td>
            </tr>
            <tr>
              <td style="padding:14px 32px;border-top:1px solid #2A2A2A;">
                <p style="color:#555555;font-size:11px;margin:0;">Este es un email automático de OperaBot — no respondas a este correo.</p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""


# ── Use cases ─────────────────────────────────────────────────────────────────

async def send_welcome_email(to_email: str, company_name: str) -> bool:
    """Sent when an admin approves a pending user."""
    safe_company = html_lib.escape(company_name)
    subject = "Tu cuenta en OperaBot ha sido aprobada"
    login_url = settings.FRONTEND_URL.rstrip("/")

    html_body = _render_template(
        heading="¡Tu cuenta ha sido aprobada!",
        message_html=(
            f"Un administrador ha aprobado tu acceso a OperaBot en <strong>{safe_company}</strong>. "
            "Ya puedes iniciar sesión y empezar a usar el asistente."
        ),
        cta_label="Iniciar sesión",
        cta_url=login_url,
    )
    text_body = (
        f"Tu cuenta en {company_name} ha sido aprobada.\n"
        f"Inicia sesión en: {login_url}"
    )
    return await send_email(to_email, subject, html_body, text_body)


async def send_ticket_resolved_email(to_email: str, ticket_question: str) -> bool:
    """Sent when an admin resolves a ticket, notifying the user of the reply."""
    safe_question = html_lib.escape(ticket_question)
    subject = "Tienes una respuesta a tu consulta"
    tickets_url = f"{settings.FRONTEND_URL.rstrip('/')}/my-tickets"

    html_body = _render_template(
        heading="El equipo ha respondido a tu consulta",
        message_html=f"Tu consulta <em>“{safe_question}”</em> ya tiene respuesta del equipo.",
        cta_label="Ver respuesta",
        cta_url=tickets_url,
    )
    text_body = (
        f"El equipo respondió tu consulta: \"{ticket_question}\"\n"
        f"Ver la respuesta en: {tickets_url}"
    )
    return await send_email(to_email, subject, html_body, text_body)

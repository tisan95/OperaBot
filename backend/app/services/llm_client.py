"""LLM client for local inference with Ollama (no cloud APIs)."""

import httpx
import logging
from typing import Any, List, Dict, Optional

from app.config import settings

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.60

# ── Intent classification ────────────────────────────────────────────────────

_GREETING_EXACT = {
    "hola", "hi", "hello", "hey", "buenas", "buenos días", "buenos dias",
    "buenas tardes", "buenas noches", "adiós", "adios", "hasta luego",
    "hasta pronto", "hasta mañana", "bye", "chao", "chau", "ok", "okay",
    "vale", "de acuerdo", "entendido", "claro", "perfecto", "muy bien",
    "gracias", "muchas gracias", "gracias por todo", "de nada", "thanks",
    "thank you", "np",
}

# Individual words that are only ever part of a greeting/ack — used for
# multi-word phrases like "hola buenos días" or "muchas gracias de nada".
_GREETING_WORDS = frozenset({
    "hola", "hi", "hello", "hey", "buenas", "buenos", "días", "dias",
    "día", "dia", "tardes", "tarde", "noches", "noche", "mañana", "manana",
    "adiós", "adios", "hasta", "luego", "pronto", "bye", "chao", "chau",
    "ok", "okay", "vale", "gracias", "muchas", "de", "nada",
    "thanks", "thank", "you", "np", "entendido", "claro", "perfecto",
    "bien", "muy",
})

_CONFIRMATION_KW = [
    "ya está", "ya funciona", "ya lo tengo", "ya entendí", "ya entiendo",
    "solucionado", "resuelto", "me ha servido", "me ha ayudado",
    "funciona ya", "ya va", "ya me funciona", "ya me sirve",
    "está funcionando", "ya está funcionando", "perfectamente, gracias",
    "genial, gracias", "muchas gracias, ya", "sí, ya está", "gracias, ya funciona",
]

_NEGATION_KW = [
    "no funciona", "no me funciona", "no sirve", "no me sirve",
    "no ayuda", "no me ayuda", "no resuelve", "no soluciona",
    "sigue sin funcionar", "sigue igual", "no es lo que busco",
    "tampoco funciona", "tampoco sirve", "no ha servido",
    "no me ha ayudado", "no está funcionando", "aún no funciona",
    "todavía no funciona", "no me ha funcionado", "no me sirve de nada",
]


def classify_intent(message: str) -> str:
    """Classify user intent from the message text.

    Returns one of: GREETING | CONFIRMATION | NEGATION | QUESTION
    """
    import re as _re
    text = message.lower().strip().rstrip("!.?")

    # Exact match — single-word or known multi-word greetings
    if text in _GREETING_EXACT:
        return "GREETING"

    # Word-level match for short multi-word greetings like "hola buenos días".
    # Strip punctuation, split into words; if every word is a greeting word → GREETING.
    clean = _re.sub(r"[,!¡¿?.]+", " ", text).strip()
    words = clean.split()
    if 1 <= len(words) <= 5 and all(w in _GREETING_WORDS for w in words):
        return "GREETING"

    # Keyword match for confirmations
    if any(kw in text for kw in _CONFIRMATION_KW):
        return "CONFIRMATION"

    # Keyword match for negations
    if any(kw in text for kw in _NEGATION_KW):
        return "NEGATION"

    return "QUESTION"


# ── Canned responses (no LLM, instant) ──────────────────────────────────────

def greeting_response() -> Dict[str, Any]:
    return {
        "answer": (
            "¡Hola! Soy OperaBot, tu asistente operacional. "
            "Puedo ayudarte a resolver dudas sobre procedimientos, "
            "manuales y preguntas frecuentes de tu empresa. "
            "¿En qué puedo ayudarte?"
        ),
        "sources": [],
        "confidence": 1.0,
        "ui_hint": None,
    }


def confirmation_response() -> Dict[str, Any]:
    return {
        "answer": "Me alegra haberte ayudado. Si tienes alguna otra duda, aquí estaré.",
        "sources": [],
        "confidence": 1.0,
        "ui_hint": None,
    }


def negation_response() -> Dict[str, Any]:
    return {
        "answer": (
            "Entendido, lamento que la respuesta no haya sido suficiente. "
            "Puedo escalar tu consulta al equipo para que te ayuden directamente."
        ),
        "sources": [],
        "confidence": 0.0,
        "ui_hint": "escalate_prompt",
    }


# ── RAG pipeline ─────────────────────────────────────────────────────────────

def _filter_by_similarity(knowledge: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
    return {
        "faqs": [f for f in knowledge.get("faqs", []) if f.get("score", 0) >= SIMILARITY_THRESHOLD],
        "documents": [d for d in knowledge.get("documents", []) if d.get("score", 0) >= SIMILARITY_THRESHOLD],
    }


def _build_context(knowledge: Dict[str, List[Dict[str, Any]]]) -> str:
    context = ""
    if knowledge.get("faqs"):
        context += "\nBASE DE CONOCIMIENTO (FAQs):\n"
        for faq in knowledge["faqs"][:3]:
            p = faq.get("payload", {})
            q, a = p.get("question", ""), p.get("answer", "")
            if q and a:
                context += f"\nPregunta: {q}\nRespuesta: {a}\n"

    if knowledge.get("documents"):
        context += "\nDOCUMENTOS DE REFERENCIA:\n"
        for doc in knowledge["documents"][:3]:
            p = doc.get("payload", {})
            text = p.get("text", "")
            filename = p.get("filename", "documento")
            if text:
                context += f"\n[{filename}]\n{text[:600]}\n"

    return context.strip() or ""


def _extract_cited_documents(knowledge: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, str]]:
    """Extract document IDs and names from RAG results for frontend preview links."""
    seen: set = set()
    cited = []
    for doc in knowledge.get("documents", []):
        payload = doc.get("payload", {})
        doc_id = payload.get("document_id")
        filename = payload.get("filename", "")
        if doc_id is not None and doc_id not in seen:
            seen.add(doc_id)
            cited.append({"id": str(doc_id), "name": filename})
    return cited


def _extract_sources(knowledge: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, str]]:
    sources: Dict[str, Dict[str, str]] = {}
    for faq in knowledge.get("faqs", []):
        q = faq.get("payload", {}).get("question", "")
        if q and (q not in sources or faq.get("score", 0) > float(sources[q]["score"])):
            sources[q] = {"type": "FAQ", "title": q, "name": q, "score": f"{faq.get('score', 0):.2f}"}
    for doc in knowledge.get("documents", []):
        name = doc.get("payload", {}).get("filename", "unknown")
        if name and (name not in sources or doc.get("score", 0) > float(sources[name]["score"])):
            sources[name] = {"type": "Document", "title": name, "name": name, "score": f"{doc.get('score', 0):.2f}"}
    return list(sources.values())


def _calculate_confidence(knowledge: Dict[str, List[Dict[str, Any]]]) -> float:
    scores = [f.get("score", 0) for f in knowledge.get("faqs", [])] + \
             [d.get("score", 0) for d in knowledge.get("documents", [])]
    return min(max(sum(scores) / len(scores), 0.0), 1.0) if scores else 0.0


# ── LLM provider adapters ────────────────────────────────────────────────────

_FALLBACK = "No he podido generar una respuesta. Por favor, intenta de nuevo."

_SYSTEM_PROMPT = """Eres OperaBot, asistente de conocimiento operacional de una empresa.
Respondes preguntas basándote en la base de conocimiento proporcionada.

REGLAS:
- Responde SIEMPRE en español
- Sé conciso: 1-3 párrafos máximo
- Integra la información naturalmente en tu respuesta
- Si usas un documento, menciónalo: "Según el manual de X..." o "En el documento Y se indica que..."
- Si usas una FAQ, responde directamente sin citar la fuente explícitamente
- NO hagas listas de fuentes al final
- Si el contexto no cubre la pregunta, dilo con honestidad y brevedad
- Tono: profesional pero cercano"""


def _build_prompt(message: str, context: str) -> str:
    if context:
        prompt = f"{_SYSTEM_PROMPT}\n\nCONTEXTO DE LA BASE DE CONOCIMIENTO:\n{context}\n\nPREGUNTA DEL USUARIO:\n{message}\n\nRespuesta:"
    else:
        prompt = f"{_SYSTEM_PROMPT}\n\nPREGUNTA DEL USUARIO:\n{message}\n\nNo tengo información específica sobre esto en la base de conocimiento. Respuesta:"
    if len(prompt) > 28000:
        logger.warning("[LLM] Prompt demasiado grande, truncando contexto.")
        prompt = f"{_SYSTEM_PROMPT}\n\nCONTEXTO (truncado):\n{context[:4000]}\n\nPREGUNTA:\n{message}\n\nRespuesta:"
    return prompt


async def _call_ollama(prompt: str, timeout: float) -> str:
    url = getattr(settings, "LLM_API_URL", None) or "http://localhost:11434/api/generate"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, json={
                "model": settings.LLM_MODEL,
                "prompt": prompt,
                "stream": False,
            })
        if resp.status_code != 200:
            logger.error(f"[LLM/ollama] {resp.status_code}: {resp.text[:200]}")
            return _FALLBACK
        return resp.json().get("response", "").strip() or _FALLBACK
    except httpx.TimeoutException:
        logger.error(f"[LLM/ollama] Timeout tras {timeout}s")
        return "La generación tardó demasiado. Por favor, intenta de nuevo."
    except httpx.ConnectError as e:
        logger.error(f"[LLM/ollama] No se puede conectar: {e}")
        return "No puedo conectar con el modelo de lenguaje. Comprueba la conexión."
    except Exception as e:
        logger.error(f"[LLM/ollama] Error inesperado: {type(e).__name__}: {e}", exc_info=True)
        return "Error interno. Por favor, intenta de nuevo."


async def _call_groq(prompt: str, timeout: float) -> str:
    url = getattr(settings, "GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
    api_key = settings.LLM_API_KEY or ""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, json={
                "model": settings.LLM_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
            }, headers={"Authorization": f"Bearer {api_key}"})
        if resp.status_code != 200:
            logger.error(f"[LLM/groq] {resp.status_code}: {resp.text[:200]}")
            return _FALLBACK
        return resp.json()["choices"][0]["message"]["content"].strip() or _FALLBACK
    except httpx.TimeoutException:
        logger.error(f"[LLM/groq] Timeout tras {timeout}s")
        return "La generación tardó demasiado. Por favor, intenta de nuevo."
    except Exception as e:
        logger.error(f"[LLM/groq] Error: {type(e).__name__}: {e}", exc_info=True)
        return "Error interno. Por favor, intenta de nuevo."


async def _call_anthropic(prompt: str, timeout: float) -> str:
    url = getattr(settings, "ANTHROPIC_API_URL", "https://api.anthropic.com/v1/messages")
    api_key = settings.LLM_API_KEY or ""
    version = getattr(settings, "ANTHROPIC_VERSION", "2023-06-01")
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, json={
                "model": settings.LLM_MODEL,
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
            }, headers={
                "x-api-key": api_key,
                "anthropic-version": version,
                "content-type": "application/json",
            })
        if resp.status_code != 200:
            logger.error(f"[LLM/anthropic] {resp.status_code}: {resp.text[:200]}")
            return _FALLBACK
        return resp.json()["content"][0]["text"].strip() or _FALLBACK
    except httpx.TimeoutException:
        logger.error(f"[LLM/anthropic] Timeout tras {timeout}s")
        return "La generación tardó demasiado. Por favor, intenta de nuevo."
    except Exception as e:
        logger.error(f"[LLM/anthropic] Error: {type(e).__name__}: {e}", exc_info=True)
        return "Error interno. Por favor, intenta de nuevo."


async def _call_llm(prompt: str, timeout: Optional[float] = None) -> str:
    """Central dispatcher: routes to the correct LLM provider based on LLM_PROVIDER."""
    t = timeout or float(getattr(settings, "LLM_TIMEOUT_SECONDS", 120) or 120)
    provider = (settings.LLM_PROVIDER or "ollama").lower()
    logger.info(f"[LLM] provider={provider} model={settings.LLM_MODEL}")
    if provider == "groq":
        return await _call_groq(prompt, t)
    if provider == "anthropic":
        return await _call_anthropic(prompt, t)
    return await _call_ollama(prompt, t)


async def _generate_with_ollama(message: str, context: str) -> str:
    """Build the prompt and call the configured LLM provider.

    The name is kept for backward compat (tests mock this function).
    Internally it now dispatches to _call_llm which routes per LLM_PROVIDER.
    """
    prompt = _build_prompt(message, context)
    logger.info(f"[LLM] Generando respuesta para: '{message[:60]}'")
    return await _call_llm(prompt)


_ESCALATION_FALLBACK = {
    "intro": "Para escalar tu consulta necesito algunos datos más:",
    "questions": [
        "¿En qué momento exacto ocurre el problema y qué mensaje de error aparece?",
        "¿Has probado alguna solución o reiniciado el sistema/aplicación?",
    ],
    "context_summary": "El usuario necesita soporte técnico.",
}


async def generate_escalation_questions(conversation: str) -> Dict[str, Any]:
    """Analyze the conversation and generate 2 specific questions for the support ticket."""
    import json, re

    prompt = f"""Eres un asistente que recoge información para un ticket de soporte técnico.

CONVERSACIÓN RECIENTE:
{conversation}

TAREA: Analiza el problema principal e infiere el contexto (software, hardware, proceso, correo, impresora, etc.).
Formula exactamente 2 preguntas específicas y concretas que ayuden al técnico a resolver el problema rápido.
Las preguntas deben ser diferentes según el tipo de problema detectado.

Devuelve ÚNICAMENTE JSON válido, sin texto antes ni después:
{{
  "intro": "Para escalar tu consulta necesito algunos datos más:",
  "questions": ["pregunta concreta 1", "pregunta concreta 2"],
  "context_summary": "resumen del problema en 1 frase corta"
}}"""

    timeout = min(float(getattr(settings, "LLM_TIMEOUT_SECONDS", 60) or 60), 45)

    try:
        raw = await _call_llm(prompt, timeout)
        # Extract the first JSON object from the response
        match = re.search(r"\{.*?\}", raw, re.DOTALL)
        if not match:
            return _ESCALATION_FALLBACK

        data = json.loads(match.group())
        if not all(k in data for k in ("intro", "questions", "context_summary")):
            return _ESCALATION_FALLBACK
        if not isinstance(data["questions"], list) or len(data["questions"]) < 1:
            return _ESCALATION_FALLBACK

        data["questions"] = [str(q) for q in data["questions"][:2]]
        if len(data["questions"]) < 2:
            data["questions"].append(_ESCALATION_FALLBACK["questions"][1])

        return data

    except Exception as e:
        logger.error(f"[LLM] Error generating escalation questions: {e}")
        return _ESCALATION_FALLBACK


async def generate_answer_with_sources(
    message: str,
    company_id: str,
    recent_rag_count: int = 0,
) -> Dict[str, Any]:
    """Generate a RAG answer. Called for QUESTION intents (and from tickets service).

    Args:
        message: User's question.
        company_id: Tenant isolation.
        recent_rag_count: Number of consecutive recent RAG exchanges without resolution.
                          Used to add a proactive follow-up after 3+ exchanges.

    Returns:
        Dict with answer, sources, confidence, ui_hint.
    """
    if not message or not isinstance(message, str):
        return {"answer": "No he entendido el mensaje.", "sources": [], "confidence": 0.0, "ui_hint": None}

    try:
        from app.services.qdrant_service import qdrant_service
        try:
            knowledge = await qdrant_service.search_knowledge(message, company_id, limit_per_collection=3)
        except Exception as e:
            logger.error(f"[RAG] Qdrant error: {e}", exc_info=True)
            knowledge = {"faqs": [], "documents": []}

        knowledge = _filter_by_similarity(knowledge)
        total = len(knowledge.get("faqs", [])) + len(knowledge.get("documents", []))

        if total == 0:
            logger.info("[RAG] Sin resultados por encima del umbral de similitud")
            return {
                "answer": "No encuentro información sobre esto en nuestra base de conocimiento.",
                "sources": [],
                "confidence": 0.0,
                "ui_hint": "escalate_prompt",
            }

        context = _build_context(knowledge)
        answer = await _generate_with_ollama(message, context)

        # After 3+ consecutive RAG exchanges, append a proactive check
        if recent_rag_count >= 2:
            answer += "\n\n¿Ha quedado resuelta tu consulta?"

        sources = _extract_sources(knowledge)
        confidence = _calculate_confidence(knowledge)
        cited_documents = _extract_cited_documents(knowledge)

        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "ui_hint": "resolution_prompt",
            "cited_documents": cited_documents,
        }

    except Exception as e:
        logger.error(f"[RAG] Error general: {e}", exc_info=True)
        return {
            "answer": "Error procesando tu pregunta. Por favor, intenta de nuevo.",
            "sources": [],
            "confidence": 0.0,
            "ui_hint": None,
        }

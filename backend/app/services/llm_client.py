"""LLM client for local inference with Ollama (no cloud APIs)."""

import httpx
import asyncio
import logging
from typing import Any, List, Dict
from app.config import settings

logger = logging.getLogger(__name__)


async def generate_answer_with_sources(message: str, company_id: str) -> Dict[str, Any]:
    """Generate an answer using RAG with sources from FAQs and Documents."""
    if not message or not isinstance(message, str):
        logger.error(f"Invalid message input: {type(message)}")
        return {
            "answer": "I didn't understand that. Could you please try again?",
            "sources": [],
            "confidence": 0.0
        }

    try:
        from app.services.qdrant_service import qdrant_service
        
        try:
            logger.info(f"[RAG] Searching knowledge base for company {company_id}")
            knowledge = qdrant_service.search_knowledge(message, company_id, limit_per_collection=3)
            logger.info(f"[RAG] Knowledge search returned {len(knowledge.get('faqs', []))} FAQs + {len(knowledge.get('documents', []))} documents")
        except Exception as e:
            logger.error(f"[RAG] Qdrant search failed: {type(e).__name__}: {e}", exc_info=True)
            knowledge = {"faqs": [], "documents": []}
        
        try:
            logger.info(f"[RAG] Building context from {len(knowledge.get('faqs', []))} FAQs and {len(knowledge.get('documents', []))} documents")
            context_text = _build_context(knowledge)
            logger.info(f"[RAG] Context built: {len(context_text)} chars")
        except Exception as e:
            logger.error(f"[RAG] Context building failed: {type(e).__name__}: {e}", exc_info=True)
            context_text = ""
        
        try:
            logger.info(f"[LLM] Starting answer generation with Ollama")
            answer = await _generate_with_ollama(message, context_text)
            logger.info(f"[LLM] Answer generated successfully: {len(answer)} chars")
        except Exception as e:
            logger.error(f"[LLM] Answer generation failed: {type(e).__name__}: {e}", exc_info=True)
            answer = "I encountered an error generating an answer. Please try again."
        
        try:
            logger.info(f"[RAG] Extracting sources from knowledge")
            sources = _extract_sources(knowledge)
            logger.info(f"[RAG] Extracted {len(sources)} sources")
        except Exception as e:
            logger.error(f"[RAG] Source extraction failed: {type(e).__name__}: {e}", exc_info=True)
            sources = []
        
        try:
            logger.info(f"[RAG] Calculating confidence score")
            confidence = _calculate_confidence(knowledge)
            logger.info(f"[RAG] Confidence: {confidence:.2f}")
        except Exception as e:
            logger.error(f"[RAG] Confidence calculation failed: {type(e).__name__}: {e}", exc_info=True)
            confidence = 0.0
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence
        }
        
    except Exception as e:
        logger.error(f"Error generating answer with sources: {e}")
        return {
            "answer": "I encountered an error processing your question. Please try again.",
            "sources": [],
            "confidence": 0.0
        }


def _build_context(knowledge: Dict[str, List[Dict[str, Any]]]) -> str:
    context = ""
    if knowledge.get("faqs"):
        for faq in knowledge["faqs"][:3]:
            payload = faq.get("payload", {})
            question = payload.get("question", "")
            answer = payload.get("answer", "")
            if question and answer:
                context += f"\nPregunta FAQ: {question}\nRespuesta FAQ: {answer}\n"
    
    if knowledge.get("documents"):
        for doc in knowledge["documents"][:3]:
            payload = doc.get("payload", {})
            text = payload.get("text", "")
            if text:
                context += f"\nFragmento de PDF:\n{text[:500]}...\n"
    
    return context


def _extract_sources(knowledge: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, str]]:
    sources = []
    seen_titles = set()  # <--- Filtro antimareos (evita duplicados)
    
    for faq in knowledge.get("faqs", []):
        payload = faq.get("payload", {})
        question = payload.get("question", "")
        # Solo lo añade si no lo ha visto antes
        if question and question not in seen_titles:
            seen_titles.add(question)
            sources.append({
                "type": "FAQ",
                "title": question,
                "score": f"{faq.get('score', 0):.2f}"
            })
            
    for doc in knowledge.get("documents", []):
        payload = doc.get("payload", {})
        filename = payload.get("filename", "unknown")
        # Solo lo añade si el PDF no está ya en la lista
        if filename and filename not in seen_titles:
            seen_titles.add(filename)
            sources.append({
                "type": "Document",
                "title": filename,
                "score": f"{doc.get('score', 0):.2f}"
            })
            
    return sources


def _calculate_confidence(knowledge: Dict[str, List[Dict[str, Any]]]) -> float:
    scores = []
    for faq in knowledge.get("faqs", []):
        scores.append(faq.get("score", 0))
    for doc in knowledge.get("documents", []):
        scores.append(doc.get("score", 0))
    if not scores:
        return 0.0
    avg_score = sum(scores) / len(scores)
    return min(max(avg_score, 0.0), 1.0)


async def _generate_with_ollama(message: str, context: str) -> str:
    try:
        if not context.strip():
            full_prompt = f"El usuario pregunta: '{message}'. Dile amablemente que no tienes información en la base de conocimientos para responder a eso."
        else:
            # AQUÍ ESTÁN LAS REGLAS DE ORO
            full_prompt = f"""Eres un asistente estricto y profesional. Tu ÚNICA fuente de verdad es la INFORMACIÓN de abajo.

REGLAS DE ORO OBLIGATORIAS:
1. Responde ÚNICA Y EXCLUSIVAMENTE con los datos de la información proporcionada.
2. Si la información es simple o parece tonta (ej. "las funciones son funciones"), responde EXACTAMENTE eso. Está prohibido añadir conocimiento técnico propio o extender la respuesta.
3. ESTÁ TOTALMENTE PROHIBIDO decir frases como "según el documento proporcionado", "en el fragmento", "el texto dice" o "lee el PDF". Debes dar la información tú mismo directamente.
4. Si la información contiene instrucciones o pasos, extráelos y redacta los pasos tú mismo claramente en una lista. No mandes al usuario a leerlos.
5. No inventes absolutamente nada.

INFORMACIÓN DISPONIBLE:
{context[:5000]}

PREGUNTA DEL USUARIO: {message}

RESPUESTA DIRECTA:"""

        logger.info(f"[LLM] Generating answer for: '{message[:50]}...' (prompt size: {len(full_prompt)} chars)")

        ollama_url = getattr(settings, 'LLM_API_URL', None) or "http://localhost:11434/api/generate"
        timeout = float(getattr(settings, 'LLM_TIMEOUT_SECONDS', 120) or 120)
        
        payload = {
            "model": settings.LLM_MODEL,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.0, # <--- Esto mata la creatividad y la invención.
                "top_k": 10,
                "top_p": 0.5
            }
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(ollama_url, json=payload)

        if response.status_code != 200:
            return "Error de conexión con la IA local."

        result = response.json()
        answer_text = result.get("response", "")
        
        if not answer_text:
            return "La IA no generó respuesta."

        return answer_text.strip()

    except Exception as e:
        logger.error(f"[LLM] Unexpected error generating answer: {type(e).__name__}: {e}", exc_info=True)
        return f"Error: {str(e)}"
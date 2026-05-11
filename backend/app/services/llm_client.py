"""LLM client for local inference with Ollama (no cloud APIs)."""

import httpx
import asyncio
import logging
from typing import Any, List, Dict
from app.config import settings
from app.models.faq import FAQ

logger = logging.getLogger(__name__)


async def generate_answer_with_sources(message: str, company_id: str) -> Dict[str, Any]:
    """Generate an answer using RAG with sources from FAQs and Documents.

    Args:
        message: The user's question/message.
        company_id: Company ID for knowledge filtering.

    Returns:
        Dict with 'answer', 'sources', and 'confidence' keys.
    """
    # Validate input
    if not message or not isinstance(message, str):
        logger.error(f"Invalid message input: {type(message)}")
        return {
            "answer": "I didn't understand that. Could you please try again?",
            "sources": [],
            "confidence": 0.0
        }

    try:
        # Search knowledge base (FAQs + Documents)
        from app.services.qdrant_service import qdrant_service
        
        try:
            logger.info(f"[RAG] Searching knowledge base for company {company_id}")
            knowledge = qdrant_service.search_knowledge(message, company_id, limit_per_collection=3)
            logger.info(f"[RAG] Knowledge search returned {len(knowledge.get('faqs', []))} FAQs + {len(knowledge.get('documents', []))} documents")
        except Exception as e:
            logger.error(f"[RAG] Qdrant search failed: {type(e).__name__}: {e}", exc_info=True)
            logger.warning(f"[RAG] Continuing with empty knowledge base (no FAQs/documents).")
            knowledge = {"faqs": [], "documents": []}
        
        # Build context from FAQs and documents
        try:
            logger.info(f"[RAG] Building context from {len(knowledge.get('faqs', []))} FAQs and {len(knowledge.get('documents', []))} documents")
            context_text = _build_context(knowledge)
            logger.info(f"[RAG] Context built: {len(context_text)} chars")
        except Exception as e:
            logger.error(f"[RAG] Context building failed: {type(e).__name__}: {e}", exc_info=True)
            logger.warning(f"[RAG] Using generic context fallback")
            context_text = "\n\nNo relevant knowledge base available. Using general knowledge."
        
        # Generate answer with context
        try:
            logger.info(f"[LLM] Starting answer generation with Ollama")
            answer = await _generate_with_ollama(message, context_text)
            logger.info(f"[LLM] Answer generated successfully: {len(answer)} chars")
        except Exception as e:
            logger.error(f"[LLM] Answer generation failed: {type(e).__name__}: {e}", exc_info=True)
            logger.warning(f"[LLM] Using error message fallback")
            answer = "I encountered an error generating an answer. Please try again."
        
        # Extract sources
        try:
            logger.info(f"[RAG] Extracting sources from knowledge")
            sources = _extract_sources(knowledge)
            logger.info(f"[RAG] Extracted {len(sources)} sources")
        except Exception as e:
            logger.error(f"[RAG] Source extraction failed: {type(e).__name__}: {e}", exc_info=True)
            sources = []
        
        # Calculate confidence based on retrieval scores
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
    """Build context string from knowledge search results."""
    context = ""
    
    # Add FAQ context
    if knowledge.get("faqs"):
        context += "\n\nKNOWLEDGE BASE (FAQs):\n"
        for faq in knowledge["faqs"][:3]:
            payload = faq.get("payload", {})
            question = payload.get("question", "")
            answer = payload.get("answer", "")
            if question and answer:
                context += f"\nQ: {question}\nA: {answer}\n"
    
    # Add document context
    if knowledge.get("documents"):
        context += "\n\nREFERENCE DOCUMENTS:\n"
        for doc in knowledge["documents"][:3]:
            payload = doc.get("payload", {})
            text = payload.get("text", "")
            filename = payload.get("filename", "unknown")
            if text:
                context += f"\n[{filename}]\n{text[:500]}...\n"
    
    return context if context.strip() else "\n\nNo relevant knowledge base available. Using general knowledge."


def _extract_sources(knowledge: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, str]]:
    """Extract sources from knowledge search results."""
    sources = []
    
    # Add FAQ sources
    for faq in knowledge.get("faqs", []):
        payload = faq.get("payload", {})
        question = payload.get("question", "")
        if question:
            sources.append({
                "type": "FAQ",
                "title": question,
                "score": f"{faq.get('score', 0):.2f}"
            })
    
    # Add document sources
    for doc in knowledge.get("documents", []):
        payload = doc.get("payload", {})
        filename = payload.get("filename", "unknown")
        sources.append({
            "type": "Document",
            "title": filename,
            "score": f"{doc.get('score', 0):.2f}"
        })
    
    return sources


def _calculate_confidence(knowledge: Dict[str, List[Dict[str, Any]]]) -> float:
    """Calculate confidence score based on retrieval quality."""
    scores = []
    
    for faq in knowledge.get("faqs", []):
        scores.append(faq.get("score", 0))
    
    for doc in knowledge.get("documents", []):
        scores.append(doc.get("score", 0))
    
    if not scores:
        return 0.0
    
    avg_score = sum(scores) / len(scores)
    # Normalize to 0-1 range (cosine similarity is already 0-1)
    return min(max(avg_score, 0.0), 1.0)


async def _generate_with_ollama(message: str, context: str) -> str:
    """Call local Ollama to generate an answer with context.

    Args:
        message: The user's question.
        context: Retrieved context from knowledge base.

    Returns:
        Generated answer text.
    """
    try:
        system_prompt = """You are OperaBot, an AI assistant for operational knowledge.
You help users find answers to common operational questions based on a knowledge base.
Be concise, helpful, and professional. If you do not know something, say so.
Always cite your sources when using information from the knowledge base."""

        full_prompt = f"""{system_prompt}

{context}

User Question: {message}

Please provide a helpful answer based on the context provided. If the context doesn't help, use your general knowledge."""

        # Limit prompt size
        if len(full_prompt) > 30000:
            logger.warning("Prompt too large. Truncating context.")
            full_prompt = f"""{system_prompt}

User Question: {message}

{context[:5000]}

Please provide a helpful answer based on the context provided."""

        logger.info(f"[LLM] Generating answer for: '{message[:50]}...' (prompt size: {len(full_prompt)} chars)")

        ollama_url = getattr(settings, 'LLM_API_URL', None) or "http://localhost:11434/api/generate"
        timeout = float(getattr(settings, 'LLM_TIMEOUT_SECONDS', 120) or 120)
        
        logger.info(f"[LLM] Ollama URL: {ollama_url}, Timeout: {timeout}s, Model: {settings.LLM_MODEL}")

        payload = {
            "model": settings.LLM_MODEL,
            "prompt": full_prompt,
            "stream": False,
        }

        logger.info(f"[LLM] Sending request to Ollama...")
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(ollama_url, json=payload)
            logger.info(f"[LLM] Ollama response status: {response.status_code}")

        if response.status_code != 200:
            logger.error(f"[LLM] Ollama error status {response.status_code}")
            logger.error(f"[LLM] Response body: {response.text}")
            return "I couldn't generate a proper answer. Please try again."

        result = response.json()
        answer_text = result.get("response", "")
        
        if not answer_text:
            logger.warning("[LLM] Empty response from Ollama")
            return "I couldn't generate a proper answer. Please try again."

        logger.info(f"[LLM] Generated answer: {len(answer_text)} chars")
        return answer_text.strip()

    except httpx.TimeoutException as e:
        logger.error(f"[LLM] Ollama timeout after {timeout}s: {e}")
        return "The answer generation took too long. Please try again."
    except httpx.ConnectError as e:
        logger.error(f"[LLM] Cannot connect to Ollama at {ollama_url}: {e}")
        return "I cannot reach the language model. Please check your connection."
    except Exception as e:
        logger.error(f"[LLM] Unexpected error generating answer: {type(e).__name__}: {e}", exc_info=True)
        return f"Error: {str(e)}"

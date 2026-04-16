"""LLM client for integrating with Gemini or other providers."""

import httpx
import asyncio
import logging
from typing import List
from app.config import settings
from app.models.faq import FAQ

logger = logging.getLogger(__name__)


async def generate_answer(message: str, faq_context: List[FAQ] = None) -> str:
    """Generate an answer using the configured LLM provider.

    Args:
        message: The user's question/message.
        faq_context: List of FAQ objects for context (optional).

    Returns:
        Generated answer text, or a fallback response if LLM is not configured.
    """
    # Validate input
    if not message or not isinstance(message, str):
        logger.error(f"Invalid message input: {type(message)}")
        return "I didn't understand that. Could you please try again?"

    # Check if LLM is configured (strict validation: no None, no empty strings)
    provider = getattr(settings, 'LLM_PROVIDER', None)
    api_key = getattr(settings, 'LLM_API_KEY', None)
    model = getattr(settings, 'LLM_MODEL', None)

    if not provider or not api_key or not model:
        missing = []
        if not provider:
            missing.append('LLM_PROVIDER')
        if not api_key:
            missing.append('LLM_API_KEY')
        if not model:
            missing.append('LLM_MODEL')
        logger.info(f"LLM not fully configured (missing: {', '.join(missing)}). Using fallback.")
        return _get_fallback_response(message)

    # Validate configuration strings are not empty after stripping
    if not provider.strip() or not api_key.strip() or not model.strip():
        logger.warning("LLM configuration contains empty strings. Using fallback.")
        return _get_fallback_response(message)

    # Attempt to use the configured provider
    provider_lower = provider.lower().strip()
    logger.info(f"LLM configured: provider={provider_lower}, model={model}")
    
    if provider_lower == "gemini":
        return await _generate_with_gemini(message, faq_context)
    else:
        # Unknown provider
        logger.warning(f"Unknown LLM provider: '{provider}'. Using fallback.")
        return _get_fallback_response(message)


async def _generate_with_gemini(message: str, faq_context: List[FAQ] = None) -> str:
    """Call Google Gemini API to generate an answer.

    Args:
        message: The user's question.
        faq_context: List of FAQ objects for context.

    Returns:
        Generated answer text. Falls back to placeholder if API fails.
    """
    logger.info(f"Starting Gemini API call with message: '{message[:50]}...'")
    
    try:
        # Build the system prompt
        system_prompt = """You are OperaBot, an AI assistant for operational knowledge. 
You help users find answers to common operational questions based on a knowledge base.
Be concise, helpful, and professional. If you don't know something, say so."""

        # Build FAQ context (limit to 5 FAQs to avoid huge prompts)
        faq_text = ""
        faq_count = 0
        if faq_context and len(faq_context) > 0:
            faq_text = "\n\nKnowledge Base (FAQs):\n"
            for faq in faq_context[:5]:
                if faq and hasattr(faq, 'question') and hasattr(faq, 'answer'):
                    category = getattr(faq, 'category', None) or "General"
                    faq_text += f"\n- [{category}] Q: {faq.question}\n  A: {faq.answer}"
                    faq_count += 1
            logger.info(f"Including {faq_count} FAQs as context")
        else:
            logger.info("No FAQ context provided")

        # Build the full prompt
        full_prompt = f"""{system_prompt}

{faq_text}

User Question: {message}

Please provide a helpful answer based on the knowledge base above if relevant, or your general knowledge."""

        # Validate prompt size (Gemini has limits)
        if len(full_prompt) > 30000:  # ~30k chars is safe
            logger.warning("Prompt too large for Gemini API. Truncating FAQ context.")
            # Rebuild with fewer FAQs
            faq_text = "\n\nKnowledge Base (FAQs):\n"
            faq_count = 0
            for faq in (faq_context[:2] if faq_context else []):
                if faq and hasattr(faq, 'question') and hasattr(faq, 'answer'):
                    category = getattr(faq, 'category', None) or "General"
                    faq_text += f"\n- [{category}] Q: {faq.question}\n  A: {faq.answer}"
                    faq_count += 1
            full_prompt = f"""{system_prompt}

{faq_text}

User Question: {message}

Please provide a helpful answer based on the knowledge base above if relevant."""
            logger.info(f"Reduced to {faq_count} FAQs due to prompt size limits")

        logger.info(f"Prompt size: {len(full_prompt)} chars")

        # Build the API request
        api_url = "https://generativelanguage.googleapis.com/v1/models/{model}:generateContent".format(
            model=settings.LLM_MODEL
        )
        api_url_with_key = f"{api_url}?key={settings.LLM_API_KEY}"
        
        logger.info(f"Calling Gemini API at model: {settings.LLM_MODEL}")

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": full_prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 1024,
            }
        }

        # Call the API
        logger.info("Making HTTP POST request to Gemini API...")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url_with_key, json=payload)

        logger.info(f"Gemini API response status: {response.status_code}")
        
        # Validate response status
        if response.status_code != 200:
            logger.error(
                f"Gemini API returned {response.status_code}: {response.text[:200]}"
            )
            return _get_fallback_response(message)

        # Parse and extract response
        try:
            result = response.json()
            logger.info(f"Gemini API response parsed successfully")
        except Exception as json_err:
            logger.error(f"Failed to parse Gemini API response: {json_err}")
            return _get_fallback_response(message)

        # Log response structure
        logger.info(f"Response keys: {list(result.keys())}")
        
        # Extract text from response
        if result.get("candidates") and len(result["candidates"]) > 0:
            logger.info(f"Found {len(result['candidates'])} candidates in response")
            content = result["candidates"][0].get("content", {})
            logger.info(f"Content keys: {list(content.keys())}")
            
            if content.get("parts") and len(content["parts"]) > 0:
                logger.info(f"Found {len(content['parts'])} parts in content")
                text = content["parts"][0].get("text", "")
                
                if text and isinstance(text, str):
                    logger.info(f"✅ Successfully extracted Gemini response: {len(text)} chars")
                    return text
                else:
                    logger.warning(f"Part text is empty or not a string: {type(text)}")
            else:
                logger.warning("No parts found in content")
        else:
            logger.warning("No candidates found in response")

        logger.warning(f"Unexpected Gemini response structure: {result}")
        return _get_fallback_response(message)

    except asyncio.TimeoutError:
        logger.error("❌ Gemini API call timed out (30s timeout exceeded)")
        return _get_fallback_response(message)
    except Exception as e:
        logger.error(f"❌ Unexpected error calling Gemini API: {type(e).__name__}: {e}", exc_info=True)
        return _get_fallback_response(message)


def _get_fallback_response(message: str) -> str:
    """Return a friendly fallback response.

    Args:
        message: The original user message.

    Returns:
        A fallback response string.
    """
    return f"Thanks for your message: '{message}'. I'm learning to respond better!"

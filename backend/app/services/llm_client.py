"""LLM client for integrating with Gemini or other providers."""

import httpx
import asyncio
import logging
from typing import Any, List
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

    provider = getattr(settings, 'LLM_PROVIDER', None)
    model = getattr(settings, 'LLM_MODEL', None)

    if not provider or not provider.strip() or not model or not model.strip():
        missing = []
        if not provider or not provider.strip():
            missing.append('LLM_PROVIDER')
        if not model or not model.strip():
            missing.append('LLM_MODEL')
        logger.info(f"LLM not fully configured (missing: {', '.join(missing)}). Using fallback.")
        return _get_fallback_response(message)

    provider_lower = provider.lower().strip()
    logger.info(f"LLM configured: provider={provider_lower}, model={model}")

    if provider_lower == "ollama":
        return await _generate_with_ollama(message, faq_context)

    api_key = getattr(settings, 'LLM_API_KEY', None)
    if not api_key or not api_key.strip():
        logger.info("LLM_API_KEY is missing for Gemini provider. Using fallback.")
        return _get_fallback_response(message)

    if provider_lower == "gemini":
        return await _generate_with_gemini(message, faq_context)

    logger.warning(f"Unknown LLM provider: '{provider}'. Using fallback.")
    return _get_fallback_response(message)


async def _generate_with_ollama(message: str, faq_context: List[FAQ] = None) -> str:
    """Call a local Ollama server to generate an answer.

    Args:
        message: The user's question.
        faq_context: List of FAQ objects for context.

    Returns:
        Generated answer text. Falls back to placeholder if Ollama fails.
    """
    logger.info(f"Starting Ollama API call with message: '{message[:50]}...'")

    try:
        system_prompt = """You are OperaBot, an AI assistant for operational knowledge.
You help users find answers to common operational questions based on a knowledge base.
Be concise, helpful, and professional. If you do not know something, say so."""

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

        full_prompt = f"""{system_prompt}

{faq_text}

User Question: {message}

Please provide a helpful answer based on the knowledge base above if relevant, or your general knowledge."""

        if len(full_prompt) > 30000:
            logger.warning("Prompt too large for Ollama API. Truncating FAQ context.")
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

        ollama_url = getattr(settings, 'LLM_API_URL', None) or "http://localhost:11434/api/generate"
        timeout = getattr(settings, 'LLM_TIMEOUT_SECONDS', 120)
        timeout_float = float(timeout) if timeout else 120.0

        payload = {
            "model": settings.LLM_MODEL,
            "prompt": full_prompt,
            "stream": False,
        }

        logger.info(f"🔥 OLLAMA REQUEST DEBUG 🔥")
        logger.info(f"  URL: {ollama_url}")
        logger.info(f"  Model: {settings.LLM_MODEL} (🚀 Micro-model: 1B parameters)")
        logger.info(f"  Timeout: {timeout_float}s")
        logger.info(f"  Payload keys: {list(payload.keys())}")
        logger.info(f"  Prompt length: {len(payload['prompt'])} chars")

        async with httpx.AsyncClient(timeout=timeout_float) as client:
            try:
                logger.info("🌐 Making HTTP POST request to Ollama...")
                response = await client.post(ollama_url, json=payload)
                logger.info(f"📡 Response received - Status: {response.status_code}")
            except httpx.TimeoutException as te:
                logger.error(f"❌ TIMEOUT at {timeout_float}s: {te}")
                raise
            except Exception as req_err:
                logger.error(f"❌ REQUEST ERROR: {type(req_err).__name__}: {req_err}")
                raise

        logger.info(f"🔥 OLLAMA RESPONSE DEBUG 🔥")
        logger.info(f"  Status Code: {response.status_code}")
        logger.info(f"  Response Headers: {dict(response.headers)}")
        logger.info(f"  Response Body Length: {len(response.text)} chars")
        logger.info(f"  Response Body (first 500 chars): {response.text[:500]}")
        
        if response.status_code != 200:
            logger.error(f"❌ OLLAMA ERROR - Status: {response.status_code}")
            logger.error(f"❌ OLLAMA ERROR - Full Response: {response.text}")
            return _get_fallback_response(message)

        try:
            result = response.json()
            logger.info(f"✅ JSON parsed successfully")
            logger.info(f"  Response keys: {list(result.keys())}")
            logger.info(f"  Response (full): {result}")
        except Exception as json_err:
            logger.error(f"❌ JSON PARSE ERROR: {type(json_err).__name__}: {json_err}")
            logger.error(f"❌ Failed to parse response: {response.text}")
            return _get_fallback_response(message)

        text = _extract_ollama_text(result)
        if text:
            logger.info(f"✅ Successfully extracted Ollama response: {len(text)} chars")
            return text

        logger.warning(f"⚠️ Unexpected Ollama response structure: {result}")
        return _get_fallback_response(message)

    except httpx.TimeoutException as timeout_err:
        logger.error(f"❌ TIMEOUT EXCEPTION - Ollama took longer than {timeout_float}s")
        logger.error(f"❌ Timeout details: {timeout_err}")
        return _get_fallback_response(message)
    except httpx.ConnectError as conn_err:
        logger.error(f"❌ CONNECTION ERROR - Cannot reach Ollama at {ollama_url}")
        logger.error(f"❌ Connection details: {type(conn_err).__name__}: {conn_err}")
        return _get_fallback_response(message)
    except Exception as e:
        logger.error(f"❌ UNEXPECTED ERROR - {type(e).__name__}: {e}")
        logger.error(f"❌ Full traceback:", exc_info=True)
        return _get_fallback_response(message)


def _extract_ollama_text(result: Any) -> str | None:
    """Extract the generated answer text from an Ollama response payload."""
    logger.info(f"🔍 EXTRACTING OLLAMA TEXT - Result type: {type(result)}")
    
    if isinstance(result, dict):
        logger.info(f"🔍 Result is a dict with keys: {list(result.keys())}")
        
        # Try direct keys
        for key in ("response", "text", "result"):
            value = result.get(key)
            logger.info(f"🔍 Trying key '{key}': {type(value)} = {value[:100] if isinstance(value, str) else value}")
            if isinstance(value, str) and value.strip():
                logger.info(f"✅ Found text at key '{key}': {len(value)} chars")
                return value.strip()

        # Try nested results
        if "results" in result and isinstance(result["results"], list):
            logger.info(f"🔍 Found 'results' list with {len(result['results'])} items")
            for idx, item in enumerate(result["results"]):
                if isinstance(item, dict):
                    logger.info(f"🔍   Item {idx} keys: {list(item.keys())}")
                    for key in ("response", "text", "result"):
                        value = item.get(key)
                        if isinstance(value, str) and value.strip():
                            logger.info(f"✅ Found text at results[{idx}]['{key}']: {len(value)} chars")
                            return value.strip()
                    content = item.get("content")
                    if isinstance(content, dict):
                        logger.info(f"🔍   Item {idx} has 'content' dict with keys: {list(content.keys())}")
                        for key in ("response", "text", "result"):
                            value = content.get(key)
                            if isinstance(value, str) and value.strip():
                                logger.info(f"✅ Found text at results[{idx}]['content']['{key}']: {len(value)} chars")
                                return value.strip()

        # Try output
        if "output" in result and isinstance(result["output"], str) and result["output"].strip():
            logger.info(f"✅ Found text at key 'output': {len(result['output'])} chars")
            return result["output"].strip()

    logger.warning(f"⚠️ Could not extract text from result: {result}")
    return None


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
        timeout = getattr(settings, 'LLM_TIMEOUT_SECONDS', 120)
        timeout_float = float(timeout) if timeout else 120.0
        logger.info(f"Making HTTP POST request to Gemini API with {timeout_float}s timeout...")
        async with httpx.AsyncClient(timeout=timeout_float) as client:
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
        logger.error(f"❌ Gemini API call timed out ({timeout_float}s timeout exceeded)")
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

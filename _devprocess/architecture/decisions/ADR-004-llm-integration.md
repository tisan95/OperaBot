# ADR-004: LLM Provider Integration & Fallback Strategy

**Status**: Accepted  
**Date**: 2026-04-15 | **Updated**: 2026-04-20  
**Author**: Architect  
**Scope**: MVP Chat RAG Pipeline

---

## Context and Problem Statement

OperaBot chat feature (FEATURE-008, FEATURE-009) requires integration with a local LLM to generate answers based on retrieved company documents. No external API calls to cloud LLM services (Gemini, OpenAI, Claude) due to privacy, cost, and latency requirements.

**Requirements**:
- Zero cloud API costs (self-hosted LLM)
- Support for context-aware generation (RAG: pass retrieved documents as context)
- <5 second response time (local inference)
- Ability to run entirely offline (no external dependencies)
- Suitable for operational question-answering with company knowledge

**Key Question**: Which local LLM for MVP with best balance of quality, speed, and resource usage?

## Decision Drivers

1. **Privacy**: No cloud API calls, all data stays on-premise
2. **Cost**: Zero cloud LLM fees (self-hosted only)
3. **Latency**: <5 sec total response time (local inference)
4. **Flexibility**: Should be able to swap local models without code changes
5. **Context Quality**: Must work well with RAG (long context windows preferred)
6. **Resource Efficiency**: Run on modest hardware (CPU or small GPU)

## Considered Options

### Option 1: Google Gemini API (Rejected)
```
Setup: Cloud API with API key

Pros:
- High quality answers
- Large context window (100K tokens)

Cons:
- Requires cloud connectivity (privacy risk)
- API costs accumulate (not zero-cost)
- External dependency (if API down, feature fails)
- Data leaves on-premise (company policy violation)
```

### Option 2: OpenAI GPT-4 API (Rejected)
```
Pros:
- Best quality answers
- Well-documented

Cons:
- Expensive API calls
- Requires internet connection
- External dependency
- Data shared with third party
```

### Option 3: Anthropic Claude API (Rejected)
```
Pros:
- Excellent reasoning
- Good documentation

Cons:
- More expensive than Gemini
- Cloud-dependent
- External API calls
- Same privacy concerns
```

### Option 4: Local LLM with Ollama (CHOSEN)
```
Setup: Ollama + Phi-3 or Llama3.2 models running locally in Docker

Pros:
- Zero cloud costs (self-hosted)
- No API keys or external connectivity needed
- All data stays on-premise (privacy compliant)
- Can run on CPU (acceptable for MVP latency)
- Easy model swaps (Phi-3 for speed, Llama3.2 for quality)
- Docker deployment for easy setup
- Can run offline completely

Cons:
- Lower quality than GPT-4 or Claude (acceptable for operational QA)
- Slightly longer latency on CPU (~3-5s, within budget)
- Self-managed (no support team, but open-source community)
```

## Decision Outcome

**Choose: Local LLM with Ollama (Phi-3 for MVP, Llama3.2 for quality)**

**Rationale**:
1. **Privacy & Compliance**: All data stays on-premise, no external API calls (critical for enterprise customer trust).
2. **Zero Cost**: No cloud API fees, completely self-hosted and free.
3. **Offline-First**: Works entirely without internet connectivity (production resilience).
4. **Model Flexibility**: Can swap between Phi-3 (fast, 3B params) for MVP and Llama3.2 (quality, 7-8B) for scaling.
5. **Docker Native**: Runs in containers alongside PostgreSQL and Qdrant (simple deployment).
6. **Latency**: Phi-3 achieves <5 sec on CPU, <2 sec on GPU (acceptable for MVP).

## Architecture

### Ollama Integration Pattern
```python
# In backend/app/services/llm_client.py

async def _generate_with_ollama(
    question: str,
    faq_context: List[FAQ] = None
) -> str:
    """Call local Ollama server at http://localhost:11434"""
    
    # Build context from retrieved FAQs
    faq_text = ""
    for faq in faq_context[:5]:
        faq_text += f"Q: {faq.question}\nA: {faq.answer}\n\n"
    
    # Call Ollama
    prompt = f"""You are OperaBot, an operational knowledge assistant.
Answer based on company knowledge base.
If you don't know, say so.

Knowledge Base:
{faq_text}

Question: {question}

Answer:"""
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi-3",  # or llama3.2 for quality
                "prompt": prompt,
                "stream": False,
            },
            timeout=5.0  # Fail fast at 5 sec
        )
    
    if response.status_code == 200:
        return response.json()["response"]
    else:
        return _get_fallback_response(question)
```

### Model Selection for MVP

**Phi-3 (3B parameters)**:
- Best for MVP (fast, low memory)
- Runs on CPU at ~2-4 sec per query
- Adequate quality for operational QA
- Model size: ~1.8 GB

**Llama3.2 (7-8B parameters)**:
- Better quality, slower (~4-6 sec on CPU)
- Use if MVP shows quality issues
- Requires more memory
- Model size: ~4-5 GB

### Confidence & Fallback Strategy
```
If Ollama is not running:
1. Timeout: <5 sec (fail fast, don't wait)
2. Fallback response: "Knowledge base unavailable. Please try again."
3. Log error for monitoring
4. Continue operation (don't crash)

If Ollama generates poor answer:
- Rely on user feedback (FEATURE-011) for quality signals
- Monitor escalation rate (target <20%)
- Consider upgrading to Llama3.2 if > 20% escalations
```

## Consequences

### Good
- Zero cloud costs (no API fees ever)
- Privacy-first (all data stays on-premise)
- Offline-capable (works without internet)
- Model flexibility (can swap Phi-3 to Llama3.2 anytime)
- Self-hosted (full control, no vendor lock-in)
- Docker deployment (same stack as PostgreSQL, Qdrant)

### Bad
- Slightly lower quality than commercial LLMs (but acceptable for MVP)
- Local CPU usage (~2-5 sec latency on CPU, acceptable for MVP)
- Operational responsibility (manage Ollama container, model updates)

### Neutral
- Need to implement fallback/retry logic (standard practice for any LLM)
- Requires Docker Compose update (Ollama service added)

## Confirmation

This decision is confirmed by:
1. **Quality Testing**: Validate Phi-3 answers meet ≥70% helpful rating (FEATURE-011 metrics)
2. **Latency Testing**: Ensure <5 sec total response time (including Ollama inference)
3. **Offline Testing**: Confirm chat works when internet is unavailable
4. **Cost Verification**: Confirm zero cloud API costs in production
5. **Escalation Testing**: Track escalation rate; if >20%, upgrade to Llama3.2
6. **Docker Verification**: Confirm Ollama container health checks pass

## Research Links

- https://ollama.ai — Ollama documentation
- https://github.com/ollama/ollama — Ollama GitHub repository
- https://huggingface.co/microsoft/phi-3 — Phi-3 model (3B parameters)
- https://huggingface.co/meta-llama/Llama-3.2 — Llama 3.2 models
- https://github.com/ollama/ollama/blob/main/docs/modelfile.md — Model configuration
- https://github.com/ollama/ollama/blob/main/docs/api.md — Ollama REST API


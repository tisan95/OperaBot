# ADR-004: LLM Provider Integration & Fallback Strategy

**Status**: Accepted  
**Date**: 2026-04-15  
**Author**: Architect  
**Scope**: MVP Chat RAG Pipeline

---

## Context and Problem Statement

OperaBot chat feature (FEATURE-008, FEATURE-009) requires integration with an external LLM to generate answers based on retrieved company documents.

**Requirements**:
- Low-cost or free tier (to keep MVP budget low, <€20/month LLM cost per company)
- Support for context-aware generation (RAG: pass retrieved documents as context)
- <5 second response time (including API call latency)
- Ability to swap providers later without rewriting application logic
- Suitable for operational question-answering (not just general knowledge)

**Key Question**: Which LLM provider for MVP, and how to design for future flexibility?

## Decision Drivers

1. **Cost**: MVP budget constraint (€500-750/month per customer, <€20 for LLM)
2. **Hypothesis H-2**: "Low-cost LLMs are good enough for operational answers with RAG"
3. **Flexibility**: Should be able to swap providers without major refactoring
4. **Latency**: <5 sec total response time (including LLM call)
5. **Context Quality**: Must work well with RAG (long context windows preferred)

## Considered Options

### Option 1: Google Gemini (Free Tier) (CHOSEN)
```
Setup: Gemini API with free tier (60 requests/minute)

Pros:
- Free tier available (good for MVP cost control)
- Large context window (100K tokens)
- Good performance on instruction-following tasks
- Supports streaming (for progressive answer generation)
- Affordable paid tier if exceeding free limits

Cons:
- Free tier rate limits (60 req/min, shared across MVP company)
- May need upgrade quickly if popular
- Less sophisticated than GPT-4 but acceptable for operational QA
```

### Option 2: Anthropic Claude (Free Tier)
```
Pros:
- Claude 3.5 Sonnet is excellent for reasoning
- Free tier available (but limited)
- Good context window

Cons:
- Free tier very limited (better to just use paid)
- Paid tier more expensive than Gemini
- Overkill for operational QA (better for complex reasoning)
```

### Option 3: OpenAI GPT-4 (Paid)
```
Pros:
- Best quality answers
- Well-documented
- Widely used

Cons:
- Expensive (not free tier)
- Doesn't fit MVP cost budget
- Overkill for operational QA
```

### Option 4: Open-Source Local LLM (Ollama, LLaMA, etc.)
```
Pros:
- Free (no API costs)
- No vendor lock-in
- Can run locally

Cons:
- Operational overhead (self-host, manage model updates)
- Weaker quality than commercial models
- Requires GPU for acceptable performance
- Not suitable for MVP timeline
```

## Decision Outcome

**Choose: Google Gemini (Free Tier, with paid tier fallback)**

**Rationale**:
1. **Cost Alignment**: Free tier supports MVP cost budget (<€20/month).
2. **Hypothesis H-2 Validation**: Gemini free tier tests if low-cost models are acceptable for operational QA.
3. **Context Window**: 100K token window is excellent for RAG (can pass multiple documents + long context).
4. **Flexibility**: If free tier insufficient, easy upgrade to paid tier without code changes.
5. **Performance**: Gemini response time typically <3 sec (within <5 sec budget for total response).

## Architecture

### LLM Abstraction Layer (Important for Future Flexibility)
```python
# In fastapi backend:

# Abstract interface for LLM providers
class LLMProvider:
    async def generate_answer(
        self,
        question: str,
        context_docs: List[str],
        confidence: float
    ) -> str:
        pass

# Gemini implementation
class GeminiProvider(LLMProvider):
    async def generate_answer(...):
        # Call Gemini API

# Future: Can add AnthropicProvider, OpenAIProvider without changing application logic
```

### Prompt Engineering for RAG
```
System prompt:
"You are an operational knowledge assistant for a warehouse/manufacturing company.
Answer questions based ONLY on the provided company procedures and documents.
If the provided information is insufficient, say 'I don't have information on this topic.'
Do NOT provide general internet knowledge or make assumptions."

User prompt:
"Question: {user_question}

Relevant company procedures:
{retrieved_documents}

Answer:"
```

### Confidence & Fallback Strategy
```
If Gemini API fails or is slow:
1. Timeout: <5 sec (fail fast, don't wait)
2. Fallback response: "I couldn't retrieve an answer right now. Please try again or escalate to a human."
3. Log error for debugging
4. No silent failures (user is informed)

If Gemini generates unhelpful answer:
- Rely on user feedback (FEATURE-011) to identify quality issues
- Monitor "escalation rate" metric (target <30%)
```

## Consequences

### Good
- Free tier MVP cost (validates cost model before scaling)
- Simple API integration (Google SDK well-documented)
- Flexibility to upgrade or switch if needed
- Large context window perfect for RAG

### Bad
- Rate limits on free tier (if MVP becomes very popular)
- Dependent on Gemini API availability (but we accept 99.5% uptime)
- Quality tier below GPT-4 (but acceptable for MVP validation of H-2)

### Neutral
- Need to implement fallback/retry logic (standard practice)

## Confirmation

This decision is confirmed by:
1. **Quality Testing**: Validate Gemini answers meet ≥75% helpful rating threshold (FEATURE-011 metrics)
2. **Cost Analysis**: Verify actual cost per company is <€20/month in pilot
3. **Latency Testing**: Ensure <5 sec total response time (including Gemini call)
4. **Rate Limit Testing**: Confirm free tier limits don't interfere with pilot usage
5. **Escalation Testing**: Track escalation rate; if >30%, may need better LLM

## Research Links

- https://ai.google.dev/gemini-api/docs — Google Gemini API documentation
- https://ai.google.dev/pricing — Gemini API pricing
- https://python.langchain.com/docs/integrations/llms/google_generativeai — LangChain + Gemini
- https://github.com/google-generativeai/google-generativeai-python — Python SDK


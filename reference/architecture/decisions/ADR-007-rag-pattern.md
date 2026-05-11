# ADR-007: RAG Pattern & LLM Prompt Engineering

**Status**: Accepted  
**Date**: 2026-04-15  
**Author**: Architect  
**Scope**: MVP Chat Q&A with Context

---

## Context and Problem Statement

OperaBot chat (FEATURE-008, FEATURE-009) uses **RAG (Retrieval-Augmented Generation)** to ground LLM answers in company knowledge, not internet.

**Key Requirement** (FEATURE-009): ≥75% of answers rated helpful by users

**RAG Pipeline**:
1. User asks question → generate embedding
2. Search vector store (Qdrant) for similar documents
3. Retrieve top 5 documents with context
4. Pass retrieved documents + question to LLM
5. LLM generates answer based on context
6. Show answer + sources + confidence to user

**Critical Questions**:
- How to structure context for LLM?
- How many documents to retrieve (token budget)?
- How to handle documents longer than context window?
- How to ensure LLM stays grounded (doesn't hallucinate)?

## Decision Drivers

1. **Hypothesis H-2**: "Low-cost LLMs + RAG can achieve ≥75% answer quality"
2. **Confidence & Trust**: Answers must be grounded (not hallucinated)
3. **Latency**: <5 sec total response time
4. **Token Budget**: Gemini free tier has rate limits, need efficient context

## RAG Design Pattern

### Document Retrieval Strategy
```
1. User question → Generate embedding (MiniLM)
2. Query Qdrant:
   - Similarity search (cosine similarity)
   - Filter by company_id
   - Optional filter by category/tags
   - Retrieve top 5-10 documents with similarity score

3. Document chunking (important!):
   - Split long documents into 512-token chunks
   - Each chunk has metadata: source document, section, category
   - Store chunks in Qdrant (not full documents)
   - When retrieved, reconstruct context (chunk + source reference)

4. Context assembly:
   - Rank retrieved chunks by similarity
   - Include top 5 chunks (total ~2,000 tokens max)
   - Preserve document structure in prompt (section headings, etc.)
```

### Prompt Template
```
SYSTEM PROMPT:
"You are OperaBot, an operational knowledge assistant for {company_name}.
You help employees answer operational questions based on company procedures.

IMPORTANT RULES:
1. ONLY answer based on the provided company procedures below.
2. If the provided procedures don't contain relevant information, say:
   'I don't have information on this topic. Please contact {expert_name} or escalate to a human.'
3. DO NOT provide general internet knowledge or make assumptions.
4. Be concise and actionable (answer should be 3-5 sentences maximum).
5. Include step-by-step instructions if applicable.

COMPANY PROCEDURES:
---
{retrieved_documents_with_sources}
---

USER QUESTION: {user_question}

ANSWER:"
```

### Example Generated Answer
```
Q: "How do I reset a forklift alarm?"

Retrieved Docs:
1. "Forklift Daily Maintenance (Section 3.2)" - similarity: 0.89
2. "Forklift Safety Procedures (Section 1.5)" - similarity: 0.87
3. "Equipment Troubleshooting Guide (Page 15)" - similarity: 0.81

LLM Answer:
"To reset a forklift alarm:
1. Turn off the forklift ignition
2. Press the red 'ALARM RESET' button on the dashboard (left side)
3. Wait 10 seconds and restart the forklift
4. If alarm persists, contact the maintenance team

Sources: Forklift Daily Maintenance (Section 3.2), Forklift Safety Procedures (Section 1.5)"

Bot Confidence: 92% (high similarity match)
```

## Document Processing Pipeline

### Admin Uploads Document
```
1. Admin uploads PDF/Word file (FEATURE-014)
2. FastAPI extracts text (using PyPDF or python-docx)
3. Text is chunked into 512-token pieces (with overlap for context)
4. Each chunk is embedded using MiniLM
5. Chunks + embeddings stored in Qdrant with metadata:
   {
     "company_id": 456,
     "document_id": "doc-789",
     "document_name": "Forklift Manual",
     "chunk_index": 0,
     "chunk_text": "...",
     "category": "Safety",
     "tags": ["forklift", "equipment"],
     "timestamp": "2026-04-15T10:00:00Z"
   }
```

### Embedding Model
```
Model: HuggingFace Sentence Transformer "all-MiniLM-L6-v2"
- 384-dimensional embeddings
- Fast (< 1 second for 512 tokens)
- Good quality for operational domain
- Can run locally or via HuggingFace API

Alternative if quality issues:
- "all-mpnet-base-v2" (768-dim, higher quality, slower)
- OpenAI embeddings API (most expensive)
```

## Handling Quality Issues (Hypothesis H-2 Validation)

### If Answer Quality < 75% Helpful
```
Possible Issues:
1. Retrieval quality (wrong documents retrieved)
   → Improve embedding model, add better chunking
   
2. LLM answer generation (doesn't follow context)
   → Refine prompt template, add stricter instructions
   
3. Document quality (source docs are unclear)
   → Encourage admins to improve documentation (analytics feedback)
   
4. Confidence calibration (confidence doesn't match quality)
   → Adjust confidence threshold calculation

Measurement:
- Track answer ratings (FEATURE-011) per question type
- Monitor escalation rate (target <30%)
- Analyze feedback: which topics have low ratings?
- Iterate on prompt + retrieval strategy
```

## Consequences

### Good
- Grounded answers (less hallucination than pure LLM)
- Transparent sources (users see what the answer is based on)
- Confidence calibration possible (match similarity to quality)
- Scalable (works with any LLM that accepts context)

### Bad
- Complexity: RAG pipeline has multiple failure points (retrieval, embedding, LLM)
- Latency: retrieval + embedding + LLM call must all fit <5 sec budget
- Document quality dependent: garbage in = garbage out

### Neutral
- Token budget: must carefully control context size to stay within limits

## Confirmation

This decision is confirmed by:
1. **Retrieval Quality Testing**: Verify ≥75% of retrieved docs are relevant (manual audit)
2. **Answer Quality Testing**: Validate ≥75% of answers rated helpful (FEATURE-011)
3. **Latency Testing**: <5 sec total response time (retrieval + LLM)
4. **Escalation Testing**: <30% of chats escalated to human
5. **Embedding Quality**: Document similarity search validates embedding model

## Research Links

- https://www.promptingguide.ai/techniques/rag — RAG technique guide
- https://github.com/langchain-ai/langchain/blob/master/docs/docs/use_cases/question_answering/index.md — LangChain RAG
- https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 — MiniLM embedding model
- https://github.com/langchain-ai/langchain/blob/master/docs/docs/modules/data_connection/document_loaders/pdf.md — PDF document loading


# ADR-003: Vector Store Selection for Semantic Search

**Status**: Accepted  
**Date**: 2026-04-15  
**Author**: Architect  
**Scope**: MVP RAG (Retrieval-Augmented Generation) Layer

---

## Context and Problem Statement

OperaBot MVP requires semantic search over company knowledge (FAQs + documents) to power the chat RAG pipeline.

**Key Requirements** (from FEATURE-009):
- Retrieve 3-5 most relevant documents/FAQs from 1,000+ documents in <3 seconds
- Support filtering by category/tags (metadata filtering)
- Scale to 10-20 companies (each with 100-1,000 documents)
- Integration with FastAPI backend
- Similarity search: find docs related to user questions

**Critical Decision**: Which vector store?
- **Qdrant**: Open-source, self-hosted, deployed locally
- **Pinecone**: Managed cloud service, pay-per-query
- **Chroma**: Simple, in-memory, good for prototyping
- **Weaviate**: Open-source, GraphQL interface

## Decision Drivers

1. **Cost**: MVP budget is tight (€500-750/month per customer)
2. **Operational Simplicity**: Don't want to manage another service if possible
3. **Integration with FastAPI**: Need seamless Python client
4. **Metadata Filtering**: Must support filtering by category/tags
5. **Future Flexibility**: Architecture should allow migration/swap later

## Considered Options

### Option 1: Qdrant (CHOSEN - Balanced)
```
Setup: Containerized (Docker), deployed alongside FastAPI in Kubernetes/Docker Compose

Pros:
- Open-source, self-hosted (no vendor lock-in)
- Built-in metadata filtering (category, tags)
- Excellent Python client (qdrant-client)
- Good performance for MVP scale (handles 1,000+ vectors easily)
- Deployable on same infra as FastAPI (reduces operational overhead)
- HNSW indexing (fast similarity search)
- Can be embedded or run as service

Cons:
- Operational responsibility: must maintain Qdrant service
- Scaling beyond 100K vectors requires tuning
- Less mature than some cloud solutions

Use Case: Good fit for MVP with self-hosted infrastructure
```

### Option 2: Pinecone (Cloud-Managed)
```
Pros:
- Fully managed (no ops overhead)
- Scales automatically
- Fast, reliable
- Good integrations with LLM libraries (LangChain, llama-index)

Cons:
- Vendor lock-in (switching costs are high)
- Pay-per-query pricing can be expensive at scale
- For MVP: overkill operational complexity
```

### Option 3: Chroma (Simple, In-Process)
```
Pros:
- Simple, minimal setup
- Good for prototyping
- Can run in-process with Python app

Cons:
- No persistence by default (requires manual setup)
- Limited metadata filtering
- Not suitable for multi-company isolation (Chroma not multi-tenant aware)
- Would require app-level isolation logic
```

### Option 4: Weaviate (Enterprise)
```
Pros:
- GraphQL interface
- Rich query capabilities
- Open-source available

Cons:
- Heavier operational footprint
- Overkill for MVP scale
- Slower prototyping
```

## Decision Outcome

**Choose: Qdrant (Self-Hosted)**

**Rationale**:
1. **Cost Control**: Self-hosted means no per-query fees. Important for MVP budget (€500-750/month per customer).
2. **Operational Simplicity**: Docker container, easy to deploy with FastAPI in Docker Compose or Kubernetes.
3. **Metadata Filtering**: Native support for filtering by category/tags (critical for retrieving relevant docs).
4. **Flexibility**: Can migrate to managed cloud later without major code changes (open standard).
5. **Performance**: HNSW indexing is proven fast for MVP scale (1,000+ documents per company).
6. **Python Integration**: qdrant-client library integrates cleanly with FastAPI + async patterns.

## Architecture

### Deployment Model
```
For MVP:
- Docker container for Qdrant (alongside FastAPI container)
- Docker Compose for local development
- Kubernetes deployment for production (later)

Data Flow:
1. Admin uploads document → FastAPI extracts text
2. FastAPI chunks text + generates embeddings (using external embedding service)
3. Embeddings stored in Qdrant with metadata (company_id, category, tags)
4. User asks chat question → FastAPI generates embedding for question
5. FastAPI queries Qdrant with embedding (filtered by company_id + optionally category)
6. Returns top 5 matching documents
7. Documents passed to LLM with user question
```

### Multi-Tenancy in Qdrant
```
Options:
A) Separate Qdrant collection per company (simple, but non-scalable)
B) Single collection, partition by company_id in metadata (better)

Decision: Option B (shared collection with company_id metadata filter)
- Qdrant supports filtering on metadata
- Query: "Find embeddings similar to X, where metadata.company_id == Y"
- Scales better as number of companies grows
```

### Embedding Model
```
Question: Which embedding model?
- OpenAI embeddings API (pay-per-embedding, high quality)
- HuggingFace embeddings (local, free, open-source)

Decision: HuggingFace embeddings (MiniLM or similar)
- Reason: Cost control (no per-embedding fees), can run locally or via API
- Trade-off: Slightly lower quality than OpenAI, but acceptable for MVP
- Flexibility: Can upgrade to OpenAI later if needed
```

## Consequences

### Good
- Cost-effective (no per-query charges)
- Flexible: can migrate to cloud later
- Good metadata filtering for company isolation + category filtering
- Simple Docker deployment

### Bad
- Operational responsibility: Qdrant service availability is our responsibility
- Scaling to 1M+ documents would require further optimization (but not a concern for MVP)
- Need to manage embedding model updates

### Neutral
- Additional service to monitor (but within Docker Compose)

## Confirmation

This decision is confirmed by:
1. **Performance Testing**: Verify <3 sec retrieval time with 1,000+ documents per company
2. **Metadata Filtering Test**: Confirm company_id filtering works correctly (security)
3. **Docker Deployment Test**: Qdrant + FastAPI in Docker Compose starts and scales correctly
4. **Embedding Quality Test**: Verify MiniLM embeddings provide acceptable relevance (>75% helpful answers)

## Research Links

- https://qdrant.tech/documentation/ — Qdrant documentation
- https://github.com/qdrant/qdrant-client-python — Python Qdrant client
- https://qdrant.tech/documentation/concepts/filtering/ — Metadata filtering
- https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 — MiniLM embedding model
- https://github.com/langchain-ai/langchain/blob/master/docs/docs/integrations/vectorstores/qdrant.md — Qdrant + LangChain integration


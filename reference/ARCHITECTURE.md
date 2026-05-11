# Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│ Frontend (Next.js 14+)                                      │
│ - Auth pages (register, login)                              │
│ - Chat interface with RAG context                           │
│ - FAQ browser with CRUD                                     │
│ - Document upload and management                            │
│ - Admin analytics dashboard                                 │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS (JWT in cookies)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ FastAPI Backend                                             │
│                                                              │
│ ┌──────────────────┬──────────────────────────────────────┐ │
│ │ API Routes       │ Services                             │ │
│ ├──────────────────┼──────────────────────────────────────┤ │
│ │ /auth/*          │ AuthService (JWT, bcrypt)            │ │
│ │ /chat/*          │ LLMClient (RAG + Ollama)             │ │
│ │ /faq/*           │ QdrantService (vector search)        │ │
│ │ /documents/*     │ DocumentService (PDF → chunks)       │ │
│ │ /admin/*         │ Analytics (system stats)             │ │
│ └──────────────────┴──────────────────────────────────────┘ │
│                                                              │
│ Middleware: CORS, Auth dependency injection                 │
└────────┬──────────────────────────────┬──────────────┬──────┘
         │                              │              │
    ┌────▼────┐                    ┌────▼──┐      ┌───▼────┐
    │PostgreSQL│                    │Qdrant │      │ Ollama  │
    │  (data)  │                    │(vectors)     │(inference)
    └──────────┘                    └────────┘     └────────┘
```

## Data Model

### Core Entities

**User**
- id (UUID)
- email (unique, encrypted)
- password (bcrypt hash)
- company_id (FK)
- role (admin | user)

**Company** (Multi-tenant isolation)
- id (UUID)
- name
- created_at

**FAQ**
- id (integer)
- company_id (FK)
- question (string)
- answer (text)
- category (string, optional)
- created_at

**Document**
- id (integer)
- company_id (FK)
- filename (string)
- file_size (bytes)
- extracted_text (text from PDF)
- vector_count (number of chunks indexed)
- upload_status (processing | completed | failed)
- created_at

**ChatMessage**
- id (integer)
- company_id, user_id (FKs)
- user_message (text)
- bot_message (text)
- confidence (0.0-1.0)
- is_fallback (boolean)
- rating (optional user feedback)
- created_at

## Key Decisions

### 1. LLM: Ollama (Local Inference)
- **Why:** Zero cloud dependencies, full data privacy, cost-effective at scale
- **Model:** llama3.2:1b (small, fast, reasonable quality)
- **Timeout:** 300 seconds (accounts for slow local inference)

### 2. Embeddings: Ollama API
- **Why:** Same local instance, no external API calls
- **Model:** nomic-embed-text (768-dim COSINE distance)
- **Storage:** Qdrant (cosine similarity)

### 3. RAG Pattern (Retrieval Augmented Generation)
```
User Query
    ↓
[1] Search FAQs + Documents (Qdrant)
    ↓
[2] Combine top K results into context
    ↓
[3] Generate answer with Ollama
    ↓
[4] Return answer + sources + confidence
```

Confidence score = (relevance_avg_of_sources + retrieval_quality) / 2

### 4. Authentication: JWT in HTTP-only Cookies
- **Why:** Secure against XSS (cannot be accessed via JavaScript)
- **Token:** Access token (1 hour) + Refresh token (7 days)
- **Extraction:** From cookies in dependency injection

### 5. Multi-tenancy: Company-scoped Data
- All queries filtered by `company_id`
- FAQs, Documents, ChatMessages isolated per company
- Users belong to exactly one company

## Deployment

### Development
```bash
docker compose up -d
uvicorn app.main:app --reload
npm run dev
```

### Production (Kubernetes-ready)
- Stateless FastAPI instances
- PostgreSQL managed database
- Qdrant deployed separately
- Ollama on GPU node
- Next.js SSR build

## Testing

- **Unit tests:** pytest (backend, >90% target)
- **Integration tests:** API endpoints with real DB
- **E2E tests:** Browser automation via Playwright
- **Test data:** Seeded with `seed.py`

## Known Limitations

1. Ollama inference is slow (1-10s per response depending on model)
2. Vector embeddings are CPU-bound
3. No streaming responses (simple request-response)
4. Single Qdrant instance (no replication)
5. No image support in document processing (PDF text only)

## Future Improvements

1. WebSocket support for streaming responses
2. Advanced caching layer (Redis)
3. Document vectors with image extraction
4. Fine-tuned local models via LoRA
5. Advanced analytics (usage trends, common questions)

# ISSUE-004 Handoff: Chat Interface with RAG Integration

**Status:** ✅ Architecture Complete & Verified  
**Date:** April 20, 2026  
**Previous Issues:** ISSUE-002 ✅, ISSUE-003 ✅  
**Next Issue:** ISSUE-005 (Admin Document Upload)

---

## What This Issue Does

Implements the core MVP feature: **AI-powered chat assistant with local LLM + RAG**.

Users can ask operational questions, get answers grounded in company knowledge (FAQs), and see the sources.

**Example Flow:**
```
User: "What's our return policy?"
    ↓
Chat API → Search FAQs (Qdrant)
    ↓
Found: FAQ-123 "Return Policy (30 days)", FAQ-456 "Return Shipping"
    ↓
Send to Ollama with context: "FAQ: Return Policy..."
    ↓
Ollama (Phi-3): "Returns accepted within 30 days if..."
    ↓
Display answer + sources to user
```

---

## Architecture Already in Place

### ✅ Infrastructure (docker-compose.yml)
- PostgreSQL (database)
- Qdrant (vector store for FAQ search)
- Ollama (local LLM)

**Start:** `docker-compose up -d`

### ✅ Backend Configuration (backend/app/config.py)
```python
LLM_PROVIDER = "ollama"
LLM_MODEL = "phi-3"
LLM_API_URL = "http://localhost:11434/api/generate"
LLM_TIMEOUT_SECONDS = 30
```

**No API keys needed** (all local).

### ✅ LLM Integration (backend/app/services/llm_client.py)
- `_generate_with_ollama()` function already implemented
- Handles timeout + fallback gracefully
- Tested with logging for debugging

### ✅ Authentication (from ISSUE-002)
- `/auth/register`, `/auth/login` working
- User context available via `get_current_user_id()` dependency
- Company context available via `get_current_company_id()` dependency

### ✅ FAQ Data (from ISSUE-003)
- FAQ model in database (question, answer, category, company_id)
- FAQs accessible via `GET /faqs` (already implemented)
- FAQs are company-scoped

---

## What You Need to Build

### 1. Chat Message Model
**File:** `backend/app/models/chat_message.py`

```python
class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True)
    company_id = Column(String, ForeignKey("companies.id"), index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    
    # Message content
    question = Column(String(2000))  # User's question
    answer = Column(Text)             # LLM's answer
    
    # Sources & metadata
    source_faq_ids = Column(JSON, default=[])  # Which FAQs were used
    confidence = Column(Float, default=0.5)    # 0.0-1.0
    
    # Feedback (for quality metrics)
    user_rating = Column(Integer, nullable=True)  # 1-5 stars
    escalated = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 2. Qdrant Service
**File:** `backend/app/services/qdrant_service.py`

```python
# Vector search for FAQs
async def search_faqs(
    query: str,
    company_id: str,
    top_k: int = 5
) -> List[FAQ]:
    """Search FAQs using semantic similarity."""
    # 1. Generate embedding for query (using MiniLM)
    # 2. Query Qdrant with metadata filter (company_id)
    # 3. Return top_k FAQs ordered by similarity
```

**Key Points:**
- Use `sentence-transformers/all-MiniLM-L6-v2` for embeddings
- Filter results by company_id (Qdrant metadata)
- Return top 5 FAQs for context

### 3. Chat API Endpoint
**File:** `backend/app/api/routes/chat.py`

```python
@router.post("/messages")
async def create_chat_message(
    request: ChatMessageCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id)
) -> ChatMessageResponse:
    """Chat endpoint: search FAQs + generate answer via Ollama."""
    
    # 1. Search FAQs (Qdrant)
    faq_context = await search_faqs(request.question, company_id)
    
    # 2. Generate answer (Ollama)
    answer = await generate_answer(request.question, faq_context)
    
    # 3. Calculate confidence (similarity scores from Qdrant)
    confidence = calculate_confidence(faq_context)
    
    # 4. Store chat message
    message = ChatMessage(
        company_id=company_id,
        user_id=user_id,
        question=request.question,
        answer=answer,
        source_faq_ids=[faq.id for faq in faq_context],
        confidence=confidence
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    
    return ChatMessageResponse.from_orm(message)
```

### 4. Chat Frontend UI
**File:** `frontend/app/(auth)/chat/page.tsx`

```typescript
// Chat interface with message history
export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  
  const handleSend = async (message: string) => {
    // POST /api/chat/messages
    // Add to messages state
    // Show answer + sources
  };
  
  return (
    <div className="chat-container">
      {/* Message history */}
      {/* Input box */}
      {/* Loading state while waiting for Ollama */}
    </div>
  );
}
```

---

## Setup Before Starting

### 1. Verify Infrastructure
```bash
docker-compose up -d

# Check services
docker ps  # All 3 containers should be running

# Check health
curl http://localhost:6333/health      # Qdrant
curl http://localhost:11434/api/tags   # Ollama
```

### 2. Pull Ollama Model (First Time Only)
```bash
docker-compose exec ollama ollama pull phi-3
# Takes 5-10 minutes (1.8 GB download)

# Verify
curl http://localhost:11434/api/tags
# Should show {"models": [{"name": "phi-3", ...}]}
```

### 3. Test Ollama Works
```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi-3",
    "prompt": "Hello!",
    "stream": false
  }'
# Should return answer within 5 seconds
```

---

## Implementation Checklist

### Phase 1: Database & Data Layer
- [ ] Create `ChatMessage` model (database schema)
- [ ] Create `ChatMessageCreate` schema (request validation)
- [ ] Create `ChatMessageResponse` schema (API response)
- [ ] Run database migration (add chat_messages table)

### Phase 2: Vector Search
- [ ] Create `qdrant_service.py` with `search_faqs()` function
- [ ] Generate embeddings using MiniLM
- [ ] Query Qdrant with company_id metadata filter
- [ ] Test vector search returns correct FAQs

### Phase 3: Chat API
- [ ] Create `backend/app/api/routes/chat.py`
- [ ] Implement `POST /api/chat/messages` endpoint
- [ ] Wire up FAQ search + LLM call
- [ ] Calculate confidence from similarity scores
- [ ] Store chat message in database
- [ ] Test end-to-end (question → answer → storage)

### Phase 4: Frontend
- [ ] Create `frontend/app/(auth)/chat/page.tsx`
- [ ] Message input box
- [ ] Send button (calls API)
- [ ] Message history display
- [ ] Sources display (which FAQs were used)
- [ ] Loading state while waiting for Ollama

### Phase 5: Testing
- [ ] Unit tests for `qdrant_service.py`
- [ ] Integration test for chat endpoint
  - Register user
  - Create FAQ
  - Send chat message
  - Verify answer returned + stored
  - Verify sources included
- [ ] Test fallback (if Ollama unavailable, show fallback response)
- [ ] Test timeout (Ollama takes >30s, get fallback)
- [ ] Multi-tenant isolation test (user can't see other company's FAQs)

---

## Important Notes

### Local LLM (Ollama)
- **No internet required** (works offline)
- **No API keys** (completely local)
- **3-5 second response** on CPU (acceptable for MVP)
- **Phi-3 model** (3B params, fast, adequate quality)
- Can upgrade to Llama3.2 later if quality issues

### Timeout Behavior
```
If Ollama doesn't respond within 30 seconds:
1. HTTPClient timeout fires
2. Function catches exception
3. Returns fallback response
4. User sees: "Knowledge base unavailable. Try again."
5. No crash, no silent failure

This prevents users waiting forever.
```

### Vector Search (Qdrant)
- Search is FAST (<1 second)
- Uses company_id filter (no cross-tenant data leakage)
- Returns top 5 FAQs by similarity
- FAQs passed to LLM as context

### Quality Expectations
- Phi-3 (3B) is adequate for MVP RAG
  - Answers are grounded in provided FAQs
  - Reduces hallucination
  - Good enough for operational QA
- If users complain → upgrade to Llama3.2 (7-8B, better quality)

---

## Architecture Decisions (Already Made)

| Decision | Value | Reference |
|----------|-------|-----------|
| LLM Provider | Ollama (local) | [ADR-004](/_devprocess/architecture/decisions/ADR-004-llm-integration.md) |
| Model | Phi-3 (3B) | Config + ADR-004 |
| Vector Store | Qdrant | [ADR-003](/_devprocess/architecture/decisions/ADR-003-vector-store.md) |
| Embeddings | MiniLM-L6-v2 | [ADR-003](/_devprocess/architecture/decisions/ADR-003-vector-store.md) |
| Auth | JWT + HTTP-only cookies | [ADR-005](/_devprocess/architecture/decisions/ADR-005-authentication.md) |
| Multi-tenancy | Company-level RLS | [ADR-002](/_devprocess/architecture/decisions/ADR-002-database-architecture.md) |

**All decisions are FINAL** (no cloud APIs, 100% local).

---

## Success Criteria (Acceptance)

- [ ] User can send a message via chat interface
- [ ] Backend searches Qdrant for relevant FAQs
- [ ] Ollama generates answer using FAQ context
- [ ] Answer includes sources (FAQ titles)
- [ ] Answer includes confidence score
- [ ] Response time < 5 seconds (Qdrant + Ollama + DB)
- [ ] Chat history stored in database
- [ ] Only company-scoped FAQs returned (no cross-tenant leakage)
- [ ] Fallback message appears if Ollama unavailable
- [ ] All tests passing

---

## Estimated Effort

**Total:** 2-3 days

- Database layer: 2-4 hours
- Qdrant integration: 4-6 hours
- Chat API: 4-6 hours
- Frontend UI: 4-6 hours
- Testing: 4-6 hours
- **Total: 20-28 hours (2-3 days @ 8-10 h/day)**

---

## After ISSUE-004

Once chat is working:

1. **ISSUE-005** (Admin Document Upload)
   - Upload FAQs from CSV/documents
   - Generate embeddings automatically
   - Ingest into Qdrant

2. **ISSUE-006** (Admin Panel)
   - User management
   - Document management
   - Analytics dashboard

---

## Documentation

- [OLLAMA-SETUP.md](/docs/OLLAMA-SETUP.md) — Ollama troubleshooting & model switching
- [SETUP-VERIFICATION.md](/SETUP-VERIFICATION.md) — Pre-implementation checklist
- [CORRECTIONS-SUMMARY.md](/CORRECTIONS-SUMMARY.md) — What changed from architecture docs
- [README.md](/README.md) — Project overview

---

## Questions?

Refer to:
- ADRs in `_devprocess/architecture/decisions/`
- ARC42 in `_devprocess/architecture/arc42/ARC42-ARCHITECTURE.md`
- Existing code in `backend/app/api/routes/auth.py` and `backend/app/api/routes/faq.py` for patterns

---

**Ready to start? Pull Phi-3 model and begin Phase 1 (Database layer).**

```bash
docker-compose exec ollama ollama pull phi-3
```

Good luck! 🚀

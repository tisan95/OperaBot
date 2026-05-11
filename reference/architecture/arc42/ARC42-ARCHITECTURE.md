# ARC42 Architecture Documentation: OperaBot MVP

**Project**: OperaBot MVP  
**Version**: 1.0  
**Date**: April 2026  
**Scope**: Minimum Viable Product  
**Status**: ✅ Architecture Ready for Development

---

## 1. Introduction and Goals

### 1.1 What is OperaBot?

OperaBot is a **B2B SaaS operational knowledge assistant** for small-to-medium enterprises (50-250 employees) in logistics and manufacturing. It provides:

- **Chat interface**: Answer operational questions in real-time using company knowledge
- **FAQ browser**: Self-serve knowledge discovery without chat friction
- **Admin panel**: Knowledge management + analytics + kanban integration
- **RAG engine**: Semantic search over company documents + LLM-powered answers

### 1.2 Requirements Overview

| Requirement | Target | Notes |
|-------------|--------|-------|
| **Adoption** | 60-70% of users in first month | Depth over breadth |
| **Answer Quality** | ≥75% rated helpful | Trust is critical |
| **Escalation Rate** | <30% | Bot handles most questions |
| **Response Time** | <5 seconds for chat | Including LLM call |
| **Concurrent Users** | 100+ per company | Cloud-based SaaS |
| **Multi-Tenancy** | Complete isolation | Row-level security |

### 1.3 Quality Goals

| Goal | Priority | Target |
|------|----------|--------|
| **Security** | P0 | No data leaks between companies |
| **Performance** | P0 | Chat <5 sec, Dashboard <3 sec |
| **Usability** | P0 | Non-technical users (warehouse staff) |
| **Scalability** | P1 | 10-20 companies in MVP, 1,000+ later |
| **Reliability** | P1 | 99.5% uptime for chat/analytics |

### 1.4 Stakeholders

| Stakeholder | Concern | Requirement |
|-------------|---------|-------------|
| **Carlos (Junior)** | Easy to use, helps solve problems | Conversational chat, mobile-responsive |
| **Laura (Expert)** | Reduces repetitive Q&A, trust in system | Quality answers, sources shown |
| **Miguel (Director)** | ROI clarity, data-driven improvement | Analytics + kanban integration |
| **Tech Lead** | Maintainable, testable, scalable | Clean architecture, documented |

---

## 3. System Scope and Context

### 3.1 Business Context

```
┌─────────────────────────────────────────────────┐
│         OperaBot MVP (This System)              │
├─────────────────────────────────────────────────┤
│  • User Panel (Chat + FAQ)                      │
│  • Admin Panel (Knowledge + Analytics)          │
│  • RAG Engine (Semantic Search + LLM)           │
│  • Authentication (JWT + Multi-Tenancy)        │
└─────────────────────────────────────────────────┘
         ↓                  ↓                 ↓
    ┌─────────┐    ┌──────────────┐    ┌────────┐
    │ Users   │    │ Admins       │    │ Tech   │
    │ (100+)  │    │ (5-10)       │    │ (GTM)  │
    └─────────┘    └──────────────┘    └────────┘

External Systems:
    • PostgreSQL (Data Store)
    • Qdrant (Vector Store)
    • Gemini API (LLM)
    • HuggingFace (Embeddings)
    • Trello API (Kanban)
```

### 3.2 Technical Context

```
┌──────────────────┐
│   Frontend       │
│  (React/Next.js) │
└────────┬─────────┘
         │ HTTPS
         ↓
┌──────────────────────────────┐
│   FastAPI Backend            │
│  • Auth (JWT + RBAC)         │
│  • FAQ/Knowledge Mgmt        │
│  • Chat & RAG Pipeline       │
│  • Analytics                 │
│  • Admin Dashboard           │
└────────┬──────────┬──────────┘
         │          │
      HTTPS    HTTP/WebSocket
         │          │
    ┌────v──────────v─────┐
    │  PostgreSQL (Main)   │
    │  (FAQ, Users, Chat)  │
    └─────────────────────┘
    
    ┌─────────────────────┐
    │  Qdrant (Vectors)   │
    │  (Embeddings)       │
    └─────────────────────┘
    
    ┌─────────────────────┐
    │  Gemini API         │
    │  (LLM Provider)     │
    └─────────────────────┘
```

---

## 4. Solution Strategy

### 4.1 Fundamental Architecture Decisions

| Decision | Solution | Rationale |
|----------|----------|-----------|
| **Backend Framework** | FastAPI | Async-first, great for LLM integration |
| **Frontend Framework** | Next.js + React | Fast development, modern UX |
| **Database** | PostgreSQL | Multi-tenancy via RLS + row-level filtering |
| **Vector Store** | Qdrant | Self-hosted, metadata filtering, cost-effective |
| **LLM Provider** | Gemini (free tier) | Low-cost, RAG-capable, flexible |
| **Auth Model** | JWT + HTTP-only cookies | Stateless, secure, scalable |
| **Multi-Tenancy** | Row-level security | Single DB per company, strong isolation |
| **RAG Pattern** | Retrieval + Context + Generation | Grounded answers, less hallucination |

### 4.2 Technology Stack

```
Backend:
  - Language: Python 3.11+
  - Framework: FastAPI
  - ORM: SQLAlchemy + SQLModel
  - Database: PostgreSQL 14+
  - Vector Store: Qdrant
  - Auth: PyJWT
  - LLM Client: Google Generative AI SDK
  - Embeddings: sentence-transformers (MiniLM)
  - API Docs: Swagger/OpenAPI (auto-generated)

Frontend:
  - Framework: Next.js 14+ (App Router)
  - Language: TypeScript
  - Styling: Tailwind CSS
  - State: React Context + Zustand (optional)
  - Real-Time: WebSocket (native browser)
  - HTTP: Fetch API + custom wrapper
  - Icons: Lucide React

DevOps:
  - Containerization: Docker
  - Orchestration: Docker Compose (local), Kubernetes (production)
  - CI/CD: GitHub Actions
  - Deployment: AWS/GCP (pending decision)
  - Monitoring: Prometheus + Grafana (Phase 2)
```

### 4.3 Architecture Pattern

**Event-Driven Chat with Async Processing**:
```
User Types Question
  ↓
FastAPI Endpoint (async)
  ├─ Extract company_id from JWT
  ├─ Generate embedding (MiniLM)
  ├─ Query Qdrant (async) → Retrieve top 5 documents
  ├─ Call Gemini LLM (async) with context
  ├─ Format answer + sources + confidence
  └─ Return response
  ↓
React Component (Next.js)
  ├─ Display answer in chat
  ├─ Show sources (clickable)
  ├─ Show confidence %
  └─ Offer escalation button
  
User Rates Answer
  ↓
FastAPI Endpoint (async)
  ├─ Store rating in PostgreSQL
  └─ Trigger analytics update

Analytics Dashboard
  ├─ Query low-rated answers
  ├─ Query unanswered questions
  ├─ Query top questions
  └─ Admin creates Trello tasks from insights
```

---

## 5. Building Block View (Components)

### 5.1 Level 1: System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    OperaBot MVP System                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐              ┌────────────────────┐  │
│  │   User Panel     │              │  Admin Panel       │  │
│  │ (FAQ + Chat)     │              │ (Knowledge + Anly) │  │
│  └────────┬─────────┘              └────────┬───────────┘  │
│           │                                  │              │
│           └──────────────┬───────────────────┘              │
│                          │                                  │
│                   ┌──────v──────┐                           │
│                   │  FastAPI    │                           │
│                   │  API Server │                           │
│                   └──────┬──────┘                           │
│                          │                                  │
│        ┌─────────────────┼─────────────────┐               │
│        │                 │                 │               │
│   ┌────v─────┐    ┌─────v────┐    ┌──────v──┐            │
│   │PostgreSQL│    │  Qdrant  │    │ Gemini  │            │
│   │(SQL DB)  │    │(Vectors) │    │(LLM)    │            │
│   └──────────┘    └──────────┘    └─────────┘            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Level 2: Backend Components

```
┌─────────────────────────────────────────────────────┐
│              FastAPI Application                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ┌────────────────────────────────────────────────┐  │
│ │  Middleware Layer                              │  │
│ │  • Auth (JWT extraction + validation)          │  │
│ │  • Tenant Context (company_id)                 │  │
│ │  • Error Handling & Logging                    │  │
│ └────────────────────────────────────────────────┘  │
│                                                     │
│ ┌────────────────────────────────────────────────┐  │
│ │  Routes / Endpoints                            │  │
│ │  ├─ /auth (login, logout, register)            │  │
│ │  ├─ /faqs (CRUD for user/admin)                │  │
│ │  ├─ /documents (upload, manage)                │  │
│ │  ├─ /chat (real-time Q&A)                      │  │
│ │  ├─ /analytics (admin dashboard)               │  │
│ │  └─ /ws (WebSocket for chat)                   │  │
│ └────────────────────────────────────────────────┘  │
│                                                     │
│ ┌────────────────────────────────────────────────┐  │
│ │  Service Layer (Business Logic)                │  │
│ │  ├─ AuthService                                │  │
│ │  ├─ FAQService                                 │  │
│ │  ├─ ChatService (RAG pipeline)                 │  │
│ │  ├─ EmbeddingService                           │  │
│ │  ├─ AnalyticsService                           │  │
│ │  └─ KanbanService (Trello integration)         │  │
│ └────────────────────────────────────────────────┘  │
│                                                     │
│ ┌────────────────────────────────────────────────┐  │
│ │  Data Layer (Database Access)                  │  │
│ │  ├─ User Repository                            │  │
│ │  ├─ FAQ Repository                             │  │
│ │  ├─ Chat History Repository                    │  │
│ │  ├─ Analytics Repository                       │  │
│ │  └─ SQLAlchemy ORM Queries                     │  │
│ └────────────────────────────────────────────────┘  │
│                                                     │
│ ┌────────────────────────────────────────────────┐  │
│ │  External Integrations                         │  │
│ │  ├─ Gemini LLM API Client                      │  │
│ │  ├─ Qdrant Vector Store Client                 │  │
│ │  ├─ Sentence-Transformers (Embeddings)        │  │
│ │  └─ Trello API Client                          │  │
│ └────────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 5.3 Level 2: Frontend Components

```
┌──────────────────────────────────────┐
│    Next.js Application               │
├──────────────────────────────────────┤
│                                      │
│ ┌────────────────────────────────┐   │
│ │  Page Layer (App Router)       │   │
│ │  ├─ /page (login)              │   │
│ │  ├─ /(auth)/dashboard          │   │
│ │  │  ├─ /faq-browser            │   │
│ │  │  └─ /chat                   │   │
│ │  └─ /(auth)/admin              │   │
│ │     ├─ /knowledge              │   │
│ │     ├─ /analytics              │   │
│ │     └─ /settings               │   │
│ └────────────────────────────────┘   │
│                                      │
│ ┌────────────────────────────────┐   │
│ │  Component Layer               │   │
│ │  ├─ FAQBrowser                 │   │
│ │  │  ├─ CategoryNav             │   │
│ │  │  ├─ SearchBar               │   │
│ │  │  └─ ArticleDisplay          │   │
│ │  ├─ Chat                       │   │
│ │  │  ├─ MessageList             │   │
│ │  │  ├─ InputField              │   │
│ │  │  ├─ AnswerDisplay           │   │
│ │  │  ├─ RatingPrompt            │   │
│ │  │  └─ EscalationButton        │   │
│ │  ├─ AdminDashboard             │   │
│ │  │  ├─ AnalyticsCards          │   │
│ │  │  ├─ UnansweredQuestions     │   │
│ │  │  ├─ LowRatedAnswers         │   │
│ │  │  └─ CreateTaskButton        │   │
│ │  └─ Shared                     │   │
│ │     ├─ Header / Nav            │   │
│ │     ├─ Forms                   │   │
│ │     ├─ Buttons                 │   │
│ │     └─ LoadingStates           │   │
│ └────────────────────────────────┘   │
│                                      │
│ ┌────────────────────────────────┐   │
│ │  Lib / Hooks Layer             │   │
│ │  ├─ useAuth                    │   │
│ │  ├─ useFetchFAQs               │   │
│ │  ├─ useChatWebSocket           │   │
│ │  ├─ useAnalytics               │   │
│ │  └─ apiClient                  │   │
│ └────────────────────────────────┘   │
│                                      │
└──────────────────────────────────────┘
```

---

## 6. Runtime View (Scenarios)

### 6.1 Chat Scenario: User Asks a Question

```
1. User Types Question in Chat Interface
   ├─ Frontend: "How do I reset a forklift alarm?"
   └─ UI shows "Thinking..." spinner

2. Frontend sends POST /api/chat
   ├─ Request body: { question: "...", conversation_id: "..." }
   └─ Includes JWT token in cookie

3. FastAPI Middleware
   ├─ Extract JWT from cookie
   ├─ Decode & validate signature
   ├─ Extract company_id (456), user_id (123), role ("user")
   └─ Set context for request

4. Chat Endpoint Handler
   ├─ Generate embedding for question (MiniLM, ~1 sec)
   ├─ Query Qdrant: top 5 similar documents
   │  └─ Filter by company_id=456
   │  └─ Return docs with similarity score
   ├─ Assemble context prompt
   ├─ Call Gemini API with context (~3 sec)
   │  ├─ Request includes retrieved documents
   │  ├─ System prompt explains constraints
   │  └─ Receive generated answer
   ├─ Calculate confidence from retrieval scores
   ├─ Store chat in PostgreSQL
   │  └─ Query + answer + sources + rating (initially empty)
   └─ Return response

5. Response Returned to Frontend
   {
     "answer": "To reset a forklift alarm: 1. Turn off...",
     "sources": [
       { "title": "Forklift Manual", "section": "3.2" },
       { "title": "Safety Procedures", "section": "1.5" }
     ],
     "confidence": 0.92,
     "escalation_available": false
   }

6. Frontend Displays Answer
   ├─ Show answer in chat bubble
   ├─ Show sources as clickable links
   ├─ Show confidence % (92%)
   └─ Offer "Was this helpful?" rating buttons

7. User Rates Answer
   ├─ User clicks "👍 Helpful" (or "👎 Not Helpful")
   └─ Frontend sends POST /api/chat/{id}/rating

8. Backend Stores Rating
   ├─ Update chat record with rating
   └─ Trigger analytics aggregation (async)
```

### 6.2 Admin Dashboard Scenario: View Analytics

```
1. Admin Opens Analytics Dashboard
   └─ Frontend: GET /admin/analytics

2. FastAPI Middleware
   └─ Extract JWT, verify role="admin"

3. Analytics Endpoint Handler
   ├─ Query PostgreSQL for aggregated metrics
   │  ├─ Top 10 unanswered questions (confidence < 50%)
   │  ├─ Top 10 low-rated answers (rating < 4)
   │  └─ Top 20 questions by volume
   │
   ├─ Format results with:
   │  ├─ Question text
   │  ├─ Frequency / rating / confidence
   │  └─ Creation buttons for each insight
   │
   └─ Return metrics

4. Frontend Displays Analytics Dashboard
   ├─ Unanswered Questions section
   │  └─ "Many questions about 'X' (0 confidence)"
   │  └─ Button: "Create FAQ for this"
   │
   ├─ Low-Rated Answers section
   │  └─ "Answer on 'Y' rated 2/5 by 3 users"
   │  └─ Button: "Edit FAQ"
   │
   └─ Top Questions section
   │  └─ "Question 'Z' asked 15 times this week"

5. Admin Clicks "Create FAQ for this" on Unanswered Question
   ├─ Modal opens: "Create New FAQ"
   ├─ Admin fills in: Title, Content, Category, Tags
   ├─ Clicks "Publish"
   └─ Frontend sends POST /api/faqs

6. Backend Creates FAQ
   └─ Store in PostgreSQL (company_id, title, content, etc.)

7. Admin Creates Kanban Task from Insight
   ├─ Admin clicks "Create Task in Trello"
   ├─ Modal opens with pre-filled task title/description
   ├─ Admin edits (optional) and clicks "Create"
   ├─ Frontend sends POST /api/kanban/create_task

8. Backend Creates Trello Card
   ├─ Validate Trello API credentials
   ├─ Call Trello API: POST /cards
   │  └─ Card title: "Create FAQ: How to reset forklift alarm"
   │  └─ Card description: "Unanswered question asked 5 times. Example: ..."
   │  └─ Card link: back to OperaBot insight
   ├─ Store reference in PostgreSQL
   └─ Return success + Trello card link
```

---

## 7. Deployment View

### 7.1 Local Development (Docker Compose)

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: dev_password
      POSTGRES_DB: operabot_dev
    volumes:
      - postgres_data:/var/lib/postgresql/data

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:password@postgres/db
      QDRANT_HOST: qdrant
      GEMINI_API_KEY: ${GEMINI_API_KEY}
    depends_on:
      - postgres
      - qdrant
    command: uvicorn main:app --reload

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    depends_on:
      - backend
```

### 7.2 Production Deployment (Kubernetes / Cloud)

```
AWS/GCP Deployment:
  
  ┌─────────────────────────────────────┐
  │     Kubernetes Cluster              │
  ├─────────────────────────────────────┤
  │                                     │
  │  ┌────────────┐  ┌────────────┐    │
  │  │ Frontend   │  │ Backend    │    │
  │  │ (Next.js)  │  │ (FastAPI)  │    │
  │  │ Pod: 3x    │  │ Pod: 2x    │    │
  │  └────────────┘  └────────────┘    │
  │                                     │
  │  ┌────────────────────────────────┐ │
  │  │ Qdrant StatefulSet             │ │
  │  │ (with persistent volume)       │ │
  │  └────────────────────────────────┘ │
  │                                     │
  └─────────────────────────────────────┘
              ↓
    ┌──────────────────────┐
    │ RDS PostgreSQL       │
    │ (Managed, Multi-AZ)  │
    └──────────────────────┘
```

---

## 8. Concepts & Cross-Cutting Concerns

### 8.1 Security

**Authentication**:
- JWT with HTTP-only cookies
- Password hashing with bcrypt (cost ≥12)
- Session timeout: 8 hours inactivity
- See ADR-005 for full strategy

**Authorization**:
- Role-based (User vs. Admin)
- Row-level security in PostgreSQL (company_id filtering)
- Middleware enforces company_id on all queries

**Data Protection**:
- HTTPS/TLS 1.3 for all traffic
- Passwords never logged
- Trello API keys encrypted at rest
- No sensitive data in JWT payload

### 8.2 Performance & Scalability

**Async Operations**:
- FastAPI + async/await for I/O (LLM, Qdrant, DB queries)
- No blocking operations in request handlers
- WebSocket for real-time chat

**Caching** (Phase 2):
- FAQ articles: Redis (1 hour TTL)
- Search indexes: Qdrant (vector DB built-in)
- Analytics: Daily aggregation (not real-time)

**Scaling**:
- Stateless backend (easy horizontal scaling)
- Load balancer in front of FastAPI pods
- Kubernetes auto-scaling based on CPU/memory

### 8.3 Resilience & Fault Handling

**External API Failures**:
- Gemini API timeout: 5 second timeout (fail fast)
- Fallback: "I couldn't retrieve an answer. Please try again."
- No silent failures (user is informed)

**Database Failures**:
- Connection pooling (SQLAlchemy)
- Retry logic for transient errors
- Health checks on startup

**Vector Store Failures**:
- Qdrant downtime: return empty results gracefully
- Fallback: "Unable to search knowledge base. Try FAQ browse."

### 8.4 Monitoring & Observability (Phase 2)

**Logs**:
- Structured JSON logging (timestamp, level, service, message)
- Log all errors, API calls, performance metrics

**Metrics**:
- Request latency (p50, p95, p99)
- Error rates by endpoint
- LLM API usage (tokens, latency, cost)
- Qdrant query performance

**Traces**:
- Distributed tracing (OpenTelemetry)
- Trace chat request from question to answer

---

## 9. Architecture Decisions (See ADRs)

| ADR | Title | Decision |
|-----|-------|----------|
| ADR-001 | Backend Framework | FastAPI |
| ADR-002 | Database Architecture | PostgreSQL with Row-Level Security |
| ADR-003 | Vector Store | Qdrant (self-hosted) |
| ADR-004 | LLM Provider | Google Gemini (free tier) |
| ADR-005 | Authentication | JWT + HTTP-only Cookies |
| ADR-006 | Frontend Framework | Next.js + React + Tailwind CSS |
| ADR-007 | RAG Pattern | Document Chunking + Semantic Search + Context |

---

## 10. Design Patterns Applied

- **Service Layer Pattern**: Business logic in services, not endpoints
- **Repository Pattern**: Data access abstraction
- **Middleware Pattern**: Auth, tenant context, error handling
- **Async/Await Pattern**: Non-blocking I/O for external APIs
- **RAG Pattern**: Retrieval + Augmented + Generation for LLM answers
- **Factory Pattern**: Service creation with dependency injection

---

## 11. Quality Attributes

| Attribute | Target | Mechanism |
|-----------|--------|-----------|
| Performance | <5 sec chat | Async + caching + efficient RAG |
| Security | No data leaks | RLS + JWT + HTTPS |
| Usability | Non-tech users | Mobile-responsive, clear UI |
| Reliability | 99.5% uptime | Health checks, graceful degradation |
| Maintainability | Clean code | Type hints, tests, docs |
| Scalability | 1,000+ companies | Stateless, horizontal scaling |

---

**END OF ARC42 DOCUMENTATION**

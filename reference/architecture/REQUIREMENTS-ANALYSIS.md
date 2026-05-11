# Architecture Requirements Analysis

**Project:** OperaBot MVP
**Scope:** MVP
**Source:** _devprocess/requirements/handoff/architect-handoff.md

## 1. Architecture Drivers

### Critical Drivers
- Multi-tenant data isolation across companies
- Trustworthy chat answers with source attribution
- Fast retrieval and search for FAQ and knowledge queries
- Secure and maintainable document ingestion
- Analytics and feedback loops for knowledge improvement

### Supporting Drivers
- Responsive frontend for non-technical operational users
- Cost-effective MVP stack with room to scale
- Clear separation of user and admin responsibilities
- Safe integration with external LLM and vector services

## 2. Requirements Mapping

### EPIC-001: User Authentication
- Backend must enforce JWT-based auth and RBAC
- Tenant context must be derived from company_id in JWT
- Secure session handling and password storage
- Impacts: auth service, middleware, database model, RLS

### EPIC-002: Chat Assistant
- Chat endpoint must run RAG pipeline with company knowledge
- Use embeddings + vector retrieval + LLM generation
- Provide answer confidence, sources, and escalation options
- Impacts: backend services, Qdrant, Gemini integration, API contract

### EPIC-003: FAQ Knowledge Base
- Create, browse, search, and categorize FAQs
- Admin can manage company-specific knowledge articles
- Search must be fast and support structured metadata
- Impacts: PostgreSQL schema, search API, frontend FAQ browser

### EPIC-004: Knowledge Improvement & Analytics
- Capture ratings, unanswered questions, and low-rated answers
- Surface analytics to admins with improvement actions
- Support Trello task creation for content updates
- Impacts: analytics storage, admin dashboard, event capture

## 3. ASRs and Constraints

### Critical ASRs
- **ASR #1: Multi-tenant data isolation** — data must never leak between companies
- **ASR #2: Trustworthy answer generation** — answers must be grounded in company knowledge
- **ASR #3: Fast search and retrieval** — query latency must support real-time use

### Moderate ASRs
- **ASR #4: Feedback-driven improvement** — capture ratings and insights for continuous quality
- **ASR #5: Secure uploads** — document ingestion must be validated and sanitized

### Constraints
- Single database for MVP with tenant isolation
- Responsive frontend on desktop and tablet
- Cost-effective LLM solution for chat assistance
- Avoid complex external integrations beyond core services

## 4. Existing Architecture Decisions

The current architecture aligns with these requirements through the following ADRs:
- `ADR-001-backend-framework.md` — FastAPI for async API and LLM integration
- `ADR-002-database-architecture.md` — PostgreSQL + RLS for tenant isolation
- `ADR-003-vector-store.md` — Qdrant for vector retrieval
- `ADR-004-llm-integration.md` — Gemini as the initial LLM provider
- `ADR-005-authentication.md` — JWT + HTTP-only cookies for secure auth
- `ADR-006-frontend-framework.md` — Next.js + Tailwind for responsive UI
- `ADR-007-rag-pattern.md` — retrieval-augmented generation for trustworthy answers

## 5. Open Questions Answered

- Retrieval layer: Qdrant selected for MVP due to metadata filtering and self-hosted cost control.
- External vector store: Qdrant chosen over embedded search for better semantic search quality.
- Role enforcement: backend enforces RBAC, frontend enforces UI access boundaries.
- Upload validation: document ingestion should use safe extraction and file type validation for MVP.

## 6. Architecture Implications

- Backend and database must carry tenant context in every request.
- Search and chat must operate with company-scoped vectors and content.
- Document ingestion must be treated as a security-sensitive entry point.
- Analytics must be captured in a way that supports admin insight and future improvement workflows.

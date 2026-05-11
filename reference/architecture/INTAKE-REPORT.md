# Architecture Intake Report

**Project:** OperaBot MVP
**Date:** 2026-04-20
**Scope:** MVP

## 1. Technology Choices

### Backend
- FastAPI for async API, validation, and OpenAPI documentation
- Python 3.11+ with SQLAlchemy / SQLModel
- PostgreSQL 14+ with row-level security (RLS)
- Qdrant vector store for semantic retrieval
- Gemini LLM API for answer generation
- JWT authentication with HTTP-only cookies

### Frontend
- Next.js 14 App Router
- TypeScript and Tailwind CSS
- React Context for auth state, optional Zustand for complex state
- Fetch API / native WebSocket for communication

## 2. Quality Attributes

- **Performance:** chat < 5 sec, search < 2 sec, dashboard < 3 sec
- **Security:** tenant isolation, strong auth, safe uploads, HTTPS only
- **Reliability:** grounded answers, repeatable retrieval pipeline, admin analytics
- **Maintainability:** modular backend services, reusable frontend components
- **Scalability:** support 100+ users per company, 1,000+ documents per company

## 3. Architecture Intake Summary

### Key Decisions
- Use a shared PostgreSQL database with RLS for tenant isolation
- Use Qdrant for vector retrieval and metadata filtering
- Use Gemini as the primary LLM provider for MVP
- Use JWT cookies for stateless auth and session security
- Use a RAG pipeline to ground chat answers and reduce hallucination

### Deployment Target
- Local dev via Docker Compose
- Production-ready architecture suitable for AWS/GCP deployment
- Future expansion path includes Kubernetes and managed services

## 4. Architectural Risks

- RLS policy misconfiguration may expose cross-tenant data
- LLM hallucination remains a risk without strong prompt and retrieval context
- Document upload parsing may introduce security risk if untrusted files are accepted
- Performance depends on Qdrant and Gemini latency; caching and async design are needed

## 5. Recommended Next Steps

1. Validate PostgreSQL RLS policies with multi-tenant tests
2. Implement safe upload and text extraction for document ingestion
3. Build the chat RAG pipeline with company-scoped Qdrant queries
4. Deliver admin analytics views for low-rated answers and unanswered questions
5. Prepare Docker Compose environment for local integration testing

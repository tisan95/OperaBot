# Architecture Plan Context

**Project:** OperaBot MVP
**Version:** 1.0
**Date:** 2026-04-20

## Overview

OperaBot MVP is a multi-tenant operational knowledge assistant with:
- user login and role-based dashboards
- FAQ search and knowledge browsing
- chat powered by retrieval-augmented generation (RAG)
- analytics and knowledge improvement workflows

## Key Architecture Principles

- **Tenant isolation** through PostgreSQL row-level security and request-scoped company_id
- **Grounded answers** via semantic retrieval from Qdrant and Gemini LLM generation
- **Secure ingestion** with validated document upload and sanitized text extraction
- **Responsive UI** through Next.js + Tailwind
- **Async-first backend** using FastAPI for external API calls and vector search

## Primary Components

### Backend
- `backend/app/main.py` — app entrypoint and router registration
- `backend/app/api/routes/` — HTTP endpoints for auth, chat, faq, analytics
- `backend/app/models/` — data models for users, faqs, companies, analytics
- `backend/app/services/` — business logic for auth, LLM, analytics
- `backend/app/db/` — database session, repository abstractions
- `backend/app/middleware.py` — tenant, auth, and error handling

### Frontend
- `frontend/app/` — page routes and layouts
- `frontend/components/` — auth, chat, faq, admin UI components
- `frontend/lib/api.ts` — API client and request helpers
- `frontend/lib/auth.ts` — auth utilities and token flow
- `frontend/styles/` — Tailwind and theme styling

### Infrastructure
- Docker Compose should orchestrate backend, frontend, Postgres, and Qdrant for local development
- Production should deploy backend as ASGI service and frontend as static asset app with CDN

## Architecture Artifacts

- `/_devprocess/architecture/decisions/ADR-001-backend-framework.md`
- `/_devprocess/architecture/decisions/ADR-002-database-architecture.md`
- `/_devprocess/architecture/decisions/ADR-003-vector-store.md`
- `/_devprocess/architecture/decisions/ADR-004-llm-integration.md`
- `/_devprocess/architecture/decisions/ADR-005-authentication.md`
- `/_devprocess/architecture/decisions/ADR-006-frontend-framework.md`
- `/_devprocess/architecture/decisions/ADR-007-rag-pattern.md`
- `/_devprocess/architecture/decisions/ADR-008-document-ingestion-security.md`

## Developer Handoff

The next developer entry point is to implement the chat RAG pipeline, tenant-aware FAQ and document search, and safe document ingestion. The architecture is already defined; start by validating the architecture decisions in code and building the minimum viable dataflow.

## Success Criteria

- Tenant separation is enforced for all user-facing data paths
- Chat answers are generated with company knowledge and sources
- FAQ browsing and search respond quickly for common queries
- Admin analytics surface low-rated answers and unanswered questions

## Notes

The architecture is designed for an MVP delivery cycle and avoids unnecessary external complexity. Future phases may introduce managed object storage, advanced analytics pipelines, and richer document ingestion workflows.

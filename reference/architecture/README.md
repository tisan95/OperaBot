# OperaBot Architecture Documentation

This folder contains all architecture design and decision records for the OperaBot MVP.

---

## 📋 Quick Navigation

### For Architects
- **[ARCHITECT-HANDOFF.md](./ARCHITECT-HANDOFF.md)** — Complete handoff to development team
  - System overview, tech stack, key decisions
  - Implementation priorities, testing strategy
  - Security considerations, deployment pipeline
  - Open questions and risks

- **[ARC42-ARCHITECTURE.md](./arc42/ARC42-ARCHITECTURE.md)** — Comprehensive architecture documentation
  - System scope and context
  - Building blocks and components (3 levels)
  - Runtime scenarios (chat, analytics)
  - Deployment and infrastructure

### For Developers
- **[PROJECT-STRUCTURE.md](./PROJECT-STRUCTURE.md)** — File organization guide
  - Backend folder structure (FastAPI)
  - Frontend folder structure (Next.js)
  - Development workflow
  - Environment setup

### For Decision Reference
- **decisions/** — All architecture decisions (MADR format)
  - ADR-001: Backend Framework (FastAPI)
  - ADR-002: Database Multi-Tenancy (PostgreSQL RLS)
  - ADR-003: Vector Store (Qdrant)
  - ADR-004: LLM Provider (Gemini)
  - ADR-005: Authentication (JWT + Cookies)
  - ADR-006: Frontend Framework (Next.js)
  - ADR-007: RAG Pattern (Semantic Search)

---

## 🚀 Start Here

**If you're a developer starting implementation:**
1. Read [ARCHITECT-HANDOFF.md](./ARCHITECT-HANDOFF.md) (5-10 min)
2. Review [PROJECT-STRUCTURE.md](./PROJECT-STRUCTURE.md) for folder layout
3. Check the relevant ADRs for context on why choices were made
4. Start with Feature-001 (User Authentication)

**If you're a new architect reviewing decisions:**
1. Read [ARCHITECT-HANDOFF.md](./ARCHITECT-HANDOFF.md) executive summary
2. Review [ARC42-ARCHITECTURE.md](./arc42/ARC42-ARCHITECTURE.md) for full system design
3. Deep-dive into specific ADRs that interest you
4. Check open questions section for future work

---

## 📊 Architecture Summary

### Three-Tier Architecture
- **Frontend**: Next.js 14 + React + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python + SQLAlchemy
- **Data**: PostgreSQL + Qdrant (vector store) + Gemini (LLM)

### Key Decisions
| Aspect | Choice | Why? |
|--------|--------|------|
| Backend | FastAPI | Async-first, great for LLM calls, rapid dev |
| Database | PostgreSQL + RLS | Cost-effective multi-tenancy, scales to 1000+ |
| Vector Store | Qdrant | Self-hosted, metadata filtering, cost control |
| LLM | Gemini Free Tier | Low cost, large context, flexible provider |
| Auth | JWT + Cookies | Stateless, secure, standard, scales horizontally |
| Frontend | Next.js | Modern, responsive, fast development |
| RAG | Semantic Search | Grounded answers, less hallucination |

### Non-Functional Requirements
- Chat response: <5 seconds
- Dashboard load: <3 seconds
- 100+ concurrent users per company
- 99.9% auth availability
- Passwords: bcrypt (cost ≥12)
- Multi-tenant isolation: Row-level security

---

## 📁 Files in This Folder

```
architecture/
├── README.md                          (this file)
├── ARCHITECT-HANDOFF.md              (handoff document for devs)
├── PROJECT-STRUCTURE.md              (folder organization guide)
├── decisions/                         (7 Architecture Decision Records)
│   ├── ADR-001-backend-framework.md
│   ├── ADR-002-database-architecture.md
│   ├── ADR-003-vector-store.md
│   ├── ADR-004-llm-integration.md
│   ├── ADR-005-authentication.md
│   ├── ADR-006-frontend-framework.md
│   └── ADR-007-rag-pattern.md
│
├── arc42/                             (comprehensive documentation)
│   └── ARC42-ARCHITECTURE.md
│
└── diagrams/                          (placeholder for Mermaid/visuals)
```

---

## 🎯 Current Status

✅ **Architecture Phase COMPLETE**

- [x] All 7 major architecture decisions made
- [x] ADRs created with full rationale and consequences
- [x] ARC42 documentation comprehensive
- [x] Project structure defined
- [x] Deployment pipeline outlined
- [x] Security considerations addressed
- [x] Testing strategy documented

**Ready for**: Developer phase (implementation)

---

## 📖 Related Documents

**In _devprocess/context/**
- `01_business-analysis.md` — Problem, users, hypotheses, KPIs
- `02_requirements.md` — Epics, Features, User Stories, NFRs

**In docs/**
- Original product documentation (00-07_*.md)

---

## ❓ Questions?

Refer to the specific ADR or ARC42 section:
- **"Why FastAPI?"** → ADR-001
- **"How does multi-tenancy work?"** → ADR-002 + ARC42 Section 3
- **"What's the chat flow?"** → ARC42 Section 6
- **"How to set up locally?"** → PROJECT-STRUCTURE.md + ARCHITECT-HANDOFF.md

---

**Last Updated**: April 15, 2026  
**Status**: Ready for Development  
**Version**: 1.0 (Architecture Approved)

# Architecture → Developer Handoff Document

**OperaBot MVP - Ready for Development Phase**

---

## 📋 Executive Summary

Architecture phase is **COMPLETE**. All major technical decisions made. Backend and frontend structures defined. Ready to hand off to developers for implementation.

**Status**: ✅ Architecture Approved  
**Date**: April 15, 2026  
**Scope**: MVP (4-6 months, 2-3 developers)

---

## 🏗️ System Architecture Summary

### Three-Tier Architecture

```
┌─────────────────────────────────────────┐
│      Frontend (React/Next.js)           │
│  • User Dashboard (FAQ + Chat)          │
│  • Admin Panel (Knowledge + Analytics)  │
│  • Responsive Mobile UI (Tailwind)      │
└────────────────┬────────────────────────┘
                 │ HTTPS + JWT
                 ↓
┌─────────────────────────────────────────┐
│   Backend (FastAPI + Python)            │
│  • Auth Service (JWT + Multi-Tenancy)   │
│  • FAQ & Knowledge Management           │
│  • Chat RAG Pipeline                    │
│  • Analytics & Kanban Integration       │
└────────────────┬────────────────────────┘
     ┌───────────┼───────────┐
     ↓           ↓           ↓
┌─────────┐ ┌────────┐ ┌──────────┐
│Postgres │ │Qdrant  │ │ Gemini   │
│(SQL DB) │ │(Vector)│ │(LLM API) │
└─────────┘ └────────┘ └──────────┘
```

---

## 🔧 Technology Stack (Final)

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI (async-first, perfect for I/O-heavy operations)
- **Database**: PostgreSQL 14+ (with Row-Level Security for multi-tenancy)
- **ORM**: SQLAlchemy + SQLModel (async support)
- **Vector Store**: Qdrant (self-hosted, in Docker)
- **Embeddings**: HuggingFace Sentence-Transformers (MiniLM-L6-v2)
- **LLM**: Google Gemini (free tier → paid tier if needed)
- **Auth**: JWT + HTTP-only Cookies (secure, stateless)
- **Testing**: pytest + fixtures

### Frontend
- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Headless UI + custom components
- **State Management**: React Context + Zustand (optional)
- **Real-Time**: WebSocket (native browser API)
- **Testing**: Jest + React Testing Library

### DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose (dev), Kubernetes (production ready)
- **CI/CD**: GitHub Actions (template provided)
- **Deployment**: AWS/GCP (infrastructure TBD)

---

## 📐 Architecture Decisions (ADRs)

**7 Architecture Decision Records created**. Key decisions:

| ADR | Title | Decision | Rationale |
|-----|-------|----------|-----------|
| **ADR-001** | Backend Framework | **FastAPI** | Async-first, great LLM integration, rapid development |
| **ADR-002** | Database Multi-Tenancy | **PostgreSQL RLS** | Single DB, cost-effective, scales to 1000+ companies |
| **ADR-003** | Vector Store | **Qdrant** | Self-hosted, metadata filtering, cost control |
| **ADR-004** | LLM Provider | **Gemini Free Tier** | Low-cost, large context window, flexible |
| **ADR-005** | Authentication | **JWT + HTTP-only Cookies** | Stateless, secure, standard approach |
| **ADR-006** | Frontend | **Next.js + React + Tailwind** | Fast development, modern UX, responsive |
| **ADR-007** | RAG Pattern | **Semantic Search + Context + LLM** | Grounded answers, transparency, less hallucination |

**All ADRs stored in**: `_devprocess/architecture/decisions/`

---

## 📊 Key NFRs (Non-Functional Requirements)

### Performance
- Chat response: **<5 seconds** (including LLM call)
- Dashboard load: **<3 seconds**
- Search: **<2 seconds**
- Login: **<5 seconds**

### Security
- Passwords: **bcrypt (cost ≥12)**
- Transport: **TLS 1.3**
- Session timeout: **8 hours inactivity**
- Data isolation: **Row-level (company_id)**
- Auth: **JWT (no server-side sessions)**

### Scalability
- Concurrent users: **100+ per company**
- Concurrent chats: **100 sessions**
- Documents: **1,000+ per company**
- Companies: **10-20 MVP → 1,000+ later**

### Availability
- Auth system: **99.9%**
- Chat system: **99.5%**
- Analytics: **99.5%**

---

## 📁 Project Structure

**Monorepo structure** (backend + frontend in one repo):

```
operabot/
├── backend/           # FastAPI app (app/, tests/, requirements.txt)
├── frontend/          # Next.js app (app/, components/, lib/, tests/)
├── docker-compose.yml # Local dev (Postgres + Qdrant + services)
├── kubernetes/        # K8s manifests (Phase 2)
└── _devprocess/       # BA, Requirements, Architecture docs
```

**Detailed structure in**: `_devprocess/architecture/PROJECT-STRUCTURE.md`

---

## �� Getting Started for Developers

### 1. Clone & Setup
```bash
git clone https://github.com/your-org/operabot.git
cd operabot

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate (Windows)
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### 2. Local Development (Docker Compose)
```bash
cd operabot
docker-compose up
# Postgres: localhost:5432
# Qdrant: localhost:6333
# Backend: localhost:8000
# Frontend: localhost:3000
```

### 3. Run Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run test
```

### 4. Code Quality
```bash
# Backend
black .                # Format
flake8 .               # Lint
mypy app/              # Type check

# Frontend
npm run lint           # ESLint
npm run format         # Prettier
```

---

## 🎯 Implementation Priorities

### Phase 1: Core (Weeks 1-6)
- [ ] User authentication + login (FEATURE-001)
- [ ] User dashboard + FAQ browser (FEATURE-002, FEATURE-005)
- [ ] FAQ CRUD + document upload (FEATURE-013, FEATURE-014)
- [ ] Chat interface + RAG integration (FEATURE-008, FEATURE-009)

### Phase 2: Quality & Analytics (Weeks 7-10)
- [ ] Answer rating + escalation (FEATURE-011, FEATURE-012)
- [ ] Admin panel + analytics (FEATURE-003, FEATURE-016)
- [ ] Kanban integration (FEATURE-017)
- [ ] Testing + bug fixes

### Phase 3: Pilot Preparation (Weeks 11-16)
- [ ] Performance optimization
- [ ] Security audit
- [ ] Documentation
- [ ] Pilot with 2-3 companies

---

## 🧪 Testing Strategy

### Backend
- **Unit Tests**: Services, utilities (mock external calls)
- **Integration Tests**: API endpoints + database
- **Coverage Goal**: >80% (critical paths >95%)

### Frontend
- **Component Tests**: Jest + React Testing Library
- **E2E Tests**: Playwright (user journeys)
- **Coverage Goal**: >70% (critical paths >90%)

### Load Testing
- Simulate 100 concurrent users
- Verify <5 sec chat response under load
- Verify Qdrant query performance

---

## 🔐 Security Considerations

### Authentication
- JWT tokens in HTTP-only cookies (XSS protection)
- HTTPS/TLS 1.3 required in production
- Session timeout: 8 hours inactivity
- Password reset via email (signed tokens)

### Authorization
- Role-based (User vs. Admin)
- Row-level security in PostgreSQL (company_id)
- Middleware enforces company isolation
- No admin operations without verification

### Data Protection
- Passwords hashed with bcrypt
- Trello API keys encrypted at rest
- No sensitive data in JWT payload
- Audit logging (Phase 2)

### External APIs
- Gemini API timeout: 5 seconds (fail fast)
- Trello API error handling (graceful fallback)
- Rate limiting (Phase 2)

---

## 📈 Monitoring & Observability (Phase 2)

**Phase 1** (MVP): Basic logging + manual monitoring

**Phase 2** (Post-MVP):
- Prometheus metrics (request latency, error rates)
- Grafana dashboards
- Distributed tracing (OpenTelemetry)
- Log aggregation (CloudWatch, Datadog)
- Alerting (PagerDuty, Slack)

---

## 🔄 Deployment Pipeline

### Local Development
```bash
docker-compose up      # All services locally
```

### Staging
```bash
git push → GitHub Actions → Run tests → Deploy to staging
```

### Production
```bash
git tag v1.0.0 → GitHub Actions → Build + Push images → Deploy to K8s
```

---

## 📚 Documentation Ready

### Technical
- ✅ ARC42 Architecture Documentation
- ✅ 7 Architecture Decision Records (ADRs)
- ✅ Project Structure Guide
- ✅ API Documentation (auto-generated Swagger from FastAPI)

### User-Facing (Phase 2)
- [ ] User Guide
- [ ] Admin Guide
- [ ] FAQ/Troubleshooting

---

## ⚠️ Open Questions & Risks

### Technical Decisions (Still Open)
1. **Cloud Provider**: AWS vs. GCP vs. Azure?
   - Impact: Infrastructure setup, cost, integrations
   - Decision needed: ASAP (affects deployment automation)

2. **Email Service**: SendGrid vs. AWS SES vs. other?
   - Impact: Password reset, notifications
   - Decision needed: Before Phase 2

3. **Analytics DB**: Use PostgreSQL or separate analytics DB (Phase 2)?
   - Impact: Query performance vs. operational complexity
   - Decision: Defer to Phase 2 if needed

### Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Gemini API quality insufficient (H-2) | Medium | High | Test in MVP, fallback to GPT-4 if needed |
| Qdrant performance issues at scale | Low | Medium | Load testing, optimization, managed service fallback |
| Multi-tenancy RLS bugs | Low | Critical | Security audit, extensive testing |
| Frontend responsiveness on warehouse phones | Medium | Medium | Mobile testing early, progressive enhancement |
| LLM cost overruns | Low | Medium | Rate limiting, usage monitoring |

---

## ✅ Quality Gate Checklist (Architecture Complete)

- [x] All Epics have Features defined
- [x] All Features have NFRs quantified
- [x] All ASRs identified and ADRs created
- [x] Technology stack chosen and documented
- [x] Project structure defined
- [x] Deployment strategy documented
- [x] Security considerations addressed
- [x] Testing strategy outlined
- [x] Open questions identified

**Status**: ✅ APPROVED FOR DEVELOPMENT

---

## 📞 Next Steps

### For Technical Lead / Architect
1. [ ] Review all 7 ADRs
2. [ ] Review ARC42 documentation
3. [ ] Decide on cloud provider (AWS/GCP)
4. [ ] Set up GitHub repository + CI/CD
5. [ ] Provision dev environment (Docker, PostgreSQL, etc.)

### For Development Team
1. [ ] Review project structure + coding standards
2. [ ] Set up local development (Docker Compose)
3. [ ] Review FEATURE-001 (User Auth) → start implementation
4. [ ] Establish testing + code review process
5. [ ] Daily standups to track progress

### For Product Owner / BA
1. [ ] Prepare pilot customer interviews
2. [ ] Create onboarding playbook
3. [ ] Plan user feedback collection (ratings, escalations)
4. [ ] Identify success metrics (adoption, quality, ROI)

---

## 📖 Key Documents

| Document | Location | Purpose |
|----------|----------|---------|
| **Business Analysis** | `_devprocess/context/01_business-analysis.md` | Problem, users, hypotheses, KPIs |
| **Requirements** | `_devprocess/context/02_requirements.md` | Epics, Features, User Stories, NFRs |
| **Architecture** | `_devprocess/architecture/ARC42-ARCHITECTURE.md` | System design, components, patterns |
| **Decisions** | `_devprocess/architecture/decisions/ADR-*.md` | 7 key architecture decisions |
| **Project Structure** | `_devprocess/architecture/PROJECT-STRUCTURE.md` | File layout, folder organization |

---

## 🎓 Helpful References

### FastAPI
- https://fastapi.tiangolo.com/
- https://fastapi.tiangolo.com/advanced/async-sql-databases/

### Next.js
- https://nextjs.org/docs
- https://nextjs.org/docs/app

### PostgreSQL Multi-Tenancy
- https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- https://github.com/ankane/multitenancy

### RAG Pattern
- https://www.promptingguide.ai/techniques/rag
- https://github.com/langchain-ai/langchain

### Qdrant
- https://qdrant.tech/documentation/

---

**END OF ARCHITECT HANDOFF DOCUMENT**

**Developer Phase Ready**: ✅ All architectural decisions made. Project structure defined. Ready to code.

**Expected Timeline**: 4-6 months for MVP with 2-3 developers.

**Success Criteria**: Ship MVP to 2-3 pilot companies by Q3 2026 with ≥75% answer quality & ≥60% adoption.

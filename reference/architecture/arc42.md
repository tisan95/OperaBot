# arc42 Architecture Documentation: Escalation System MVP

> **Project:** OperaBot - Escalation System
> **Scope:** MVP (Production-ready)
> **Created:** 2026-04-23
> **Status:** Draft (Proposals pending approval)

---

## 1. Introduction and Goals

### 1.1 Requirements Overview

From Business Analysis and Requirements Engineering:

**Problem:** Users with failed chat queries have no escalation mechanism. Unresolved queries disappear without being captured for improvement.

**Solution:** Escalation System enables users to escalate failed queries to admins, who can respond, convert to FAQ, or discard.

**Scope (MVP):**
- User-initiated escalation from chat UI
- Admin escalations dashboard
- Response, convert-to-FAQ, discard actions
- Confidence-based escalation triggering

**Exclusions (Future):**
- Email notifications
- SLA tracking
- Escalation assignment to specific admins
- Comments/threads

### 1.2 Quality Goals

| Priority | Quality Goal | Measurement |
|----------|--------------|-------------|
| 1 | Security: Data isolation by company | RLS policies + unit tests verify isolation |
| 2 | Reliability: FAQ data not lost on Qdrant failure | Async vectorization with retry queue |
| 3 | Usability: Escalation appears only when needed | Confidence threshold <0.3 on responses |
| 4 | Performance: Escalation creation <100ms | Response time monitoring |
| 5 | Scalability: Support 100+ escalations/day per tenant | No blocking operations, async vectorization |

### 1.3 Stakeholders

| Stakeholder | Role | Interest | Influence |
|------------|------|----------|-----------|
| **Sarah (User)** | Regular user asking questions | Escalate unresolved queries quickly | High (daily usage) |
| **Marcus (Admin)** | Knowledge base manager | Manage escalations, create FAQs | High (resolves escalations) |
| **Platform Team** | DevOps/SRE | System reliability, monitoring | High (runs infrastructure) |
| **Compliance** | Security/Legal | Data isolation, multi-tenancy | Medium (audit requirements) |

---

## 2. Constraints

### 2.1 Technical Constraints

| Constraint | Background | Impact |
|-----------|-----------|--------|
| PostgreSQL database | Existing OperaBot infrastructure uses PostgreSQL | Must implement RLS policies; cannot use alternative databases |
| Qdrant vector store | Existing integration for FAQ vectorization | Vectorization failures must be handled gracefully |
| JWT authentication | Existing OperaBot auth system | company_id extracted from JWT token; must validate correctness |
| FastAPI framework | Backend is FastAPI | Escalation endpoints follow FastAPI patterns |
| Next.js frontend | Frontend is Next.js with Tailwind CSS | UI components use existing patterns; cannot modify layout.tsx or sidebar.css |
| Multi-tenancy | Existing system is multi-tenant | Escalation table must enforce company-level isolation |

### 2.2 Organizational Constraints

| Constraint | Background | Impact |
|-----------|-----------|--------|
| MVP scope | Project must deliver within 9-11 days | No email notifications, SLA tracking, or assignment workflows in this iteration |
| Existing codebase | Architecture is stable and shouldn't change | New escalation system integrates additively; does not refactor existing layers |
| No breaking changes | Users and admins currently on stable system | Escalation system adds optional feature; doesn't modify chat or FAQ behavior |

---

## 3. Context and Scope

### 3.1 Business Context

```
+---------------------+
|     End Users       |  Chat with questions
|  (Sarah, others)    |
+----------+----------+
           |
           | Posts chat query
           v
    +-----------+
    |  OperaBot |  Escalation System
    |  ChatUI   |  (this project)
    +-----------+
           |
           | If confidence <0.3:
           |   "Escalar Consulta" button appears
           |
           v
    +-----------+         Creates
    | Escalation|-------> Escalation ticket
    | Button   |
    +-----------+
           |
           | Escalation stored in DB
           v
    +-----------+
    |  Admin   |  Reviews escalations
    |  Marcus  |  Resolves/Converts/Discards
    +-----------+
```

### 3.2 Technical Context

| Interface | Protocol | Direction | Purpose |
|-----------|----------|-----------|---------|
| Chat Endpoint | REST/JSON | Inbound | Frontend requests chat response; backend returns `escalation_available` flag |
| Escalation Creation | REST/JSON POST | Inbound | Frontend submits escalation; backend creates record |
| Escalation List | REST/JSON GET | Inbound | Admin dashboard fetches pending escalations |
| Escalation Update | REST/JSON PUT | Inbound | Admin responds/converts/discards escalation |
| FAQ Service | Direct Python | Internal | When escalation converted to FAQ, vectorization triggered |
| Qdrant | gRPC/HTTP | Outbound | Vectorization sends embeddings to Qdrant |
| PostgreSQL | psycopg2 | Outbound | All escalation CRUD operations |

---

## 4. Solution Strategy

### 4.1 Technology Decisions

| Decision | Technology | ADR Reference | Rationale |
|----------|-----------|---------------|-----------|
| **Data Isolation** | PostgreSQL RLS + App-layer filters | ADR-001 | Defense in depth: database RLS + application filters |
| **Vectorization Failure Handling** | Async job queue (Celery/RQ) | ADR-002 | Non-blocking, built-in retry mechanism |
| **Confidence Threshold** | Dynamic config (default 0.3) | ADR-003 | Tunable at runtime; based on BA hypothesis H-05 |
| **Database** | PostgreSQL (existing) | Inherited | No change from existing OperaBot |
| **API Framework** | FastAPI (existing) | Inherited | No change from existing OperaBot |
| **Frontend** | Next.js + Tailwind CSS (existing) | Inherited | No change from existing OperaBot |

### 4.2 Architecture Style

**Pattern:** Modular Monolith

The Escalation System integrates into the existing OperaBot monolith:
- Backend: FastAPI routes added to `/app/api/routes/escalations.py`
- Frontend: React components added to `/app/(auth)/admin/escalations/` and `/components/Escalation/`
- Database: New `escalations` table, no microservices
- Job Queue: Background vectorization via Celery/RQ (simple, integrated)

**Rationale:** MVP scope does not justify microservices. Monolith scales well up to current volumes (100+ escalations/day per tenant).

### 4.3 Quality Approach

| Quality Goal | Approach |
|--------------|----------|
| **Security** | RLS policies + application-layer filters; unit tests verify multi-tenant isolation |
| **Reliability** | Async vectorization with retry queue; dead-letter monitoring for failed jobs |
| **Usability** | Confidence threshold based on BA hypothesis; dashboard provides escalation status |
| **Performance** | Escalation creation <100ms (no blocking); vectorization async |
| **Scalability** | No synchronous blocking; background job queue handles volume spikes |

---

## 5. Building Block View (C4 Model)

### Level 1: System Context

```
+---------------------+
|   Sarah (User)      |
+----------+----------+
           |
           | Uses
           v
    +-------------------------------------------+
    |          OperaBot System                 |
    |  (Chat, FAQs, Escalations)              |
    +-------------------------------------------+
           |
           | Uses
           |
    +---------------------+
    |  External Systems  |
    |  - Qdrant (RAG)    |
    |  - PostgreSQL      |
    +---------------------+
```

### Level 2: Containers (Components)

```
+-----------+
| Next.js   |
| Frontend  |  Chat UI + Escalation UI + Admin Dashboard
+-----------+
     |
     | REST API
     |
+-----------+
| FastAPI   |
| Backend   |  /chat, /escalations routes
+-----------+
     |
     +------> PostgreSQL      (escalations, users, faqs tables)
     |
     +------> Qdrant          (vector embeddings)
     |
     +------> Job Queue       (Celery/RQ for async vectorization)
     |        (Redis for queue storage)
```

### Level 3: Components (Backend Detail)

```
FastAPI Backend:

+------------------------------------------+
| /api/routes/chat.py                     |
|  - POST /chat                           |
|  - Returns: message, confidence,        |
|             escalation_available        |
+------------------------------------------+

+------------------------------------------+
| /api/routes/escalations.py              |
|  - POST /escalations (create)           |
|  - GET /escalations (list for admin)    |
|  - PUT /escalations/{id}/respond       |
|  - PUT /escalations/{id}/convert-faq   |
|  - PUT /escalations/{id}/discard       |
+------------------------------------------+

+------------------------------------------+
| /api/schemas/escalation.py              |
|  - EscalationCreate (input schema)      |
|  - EscalationResponse (output schema)   |
|  - Validation rules                     |
+------------------------------------------+

+------------------------------------------+
| /models/escalation.py                   |
|  - Escalation model (ORM)               |
|  - Relationships: User, Company, FAQ    |
|  - Status field: pending|responded|...  |
+------------------------------------------+

+------------------------------------------+
| /services/escalation_service.py         |
|  - Business logic: create, update, etc. |
|  - RBAC checks: user can only see own   |
|  - Admin can see all (for their company)|
+------------------------------------------+

+------------------------------------------+
| /tasks/vectorization.py (Celery/RQ)    |
|  - Task: vectorize_faq(faq_id)         |
|  - Retries on failure (up to 3 times)  |
|  - Stores vectors in Qdrant            |
+------------------------------------------+
```

---

## 6. Runtime View (Sequence Diagrams)

### Scenario 1: User Escalates Failed Query

```
Sarah                Chat UI            Backend         Database
  |                    |                  |              |
  |-- Chat Query ----->|                  |              |
  |                    |-- POST /chat --->|              |
  |                    |                  |-- Query FAQs |
  |                    |                  |<- Low conf  -|
  |<--- Response ------|<- JSON (conf<0.3)|              |
  |  (confidence 0.2)  |  escalation_     |              |
  |  "Escalation Btn"  |   available=true |              |
  |                    |                  |              |
  |-- Click "Escalar" -|                  |              |
  |   (enters notes)   |                  |              |
  |                    |-- POST /escalations ---------->|
  |                    |   {query, notes}               |
  |                    |                  |-- INSERT    |
  |                    |<- {id, status} -|<- Saved ----+
  |<- Toast confirm ---|                  |              |
  | "Escalation sent"  |                  |              |
```

### Scenario 2: Admin Converts Escalation to FAQ

```
Marcus             Dashboard          Backend         Database    Qdrant    Job Queue
  |                    |                |              |           |         |
  |-- View Dashboard ->|                |              |           |         |
  |                    |-- GET /escalations---------->|           |         |
  |                    |<- [Escalations]<- SELECT --<+           |         |
  |                    |                |              |           |         |
  |-- Click Row ----->|                |              |           |         |
  | (view details)     |                |              |           |         |
  |                    |-- GET /escalations/{id}---->|           |         |
  |                    |<- Full details<- SELECT --<+           |         |
  |                    |                |              |           |         |
  |-- Click "Crear FAQ"->Modal opens    |              |           |         |
  |   (fills Q & A)    |                |              |           |         |
  |-- Submit ------->|-- PUT /escalations/{id}/convert-faq --->| |         |
  |                    |                |              |           |         |
  |                    |                |-- INSERT faq |-- OK --+         |
  |                    |                |-- UPDATE escalation_status      |
  |                    |                |-- ENQUEUE vectorize_faq(faq) ---->|
  |                    |                |<- Job queued -<-                |
  |                    |<- {status: "created, vectorization pending"} <-|
  |<- Toast: "FAQ created" <-           |              |           |         |
  |  "Searching in 10s"                 |              |           |         |
  |                    |                |              |           |         |
  [Background job runs after 1-2 seconds]             |         |
  |                    |                |              |           |         |
  |                    |  [Job consumes task] -------->         |
  |                    |                |              |           |
  |                    |                |-- Generate embeddings -->|
  |                    |                |<- Vectors ----<+       |
  |                    |                |-- Store vectors      |
  |                    |                |<- Success ----<+       |
  |                    |                |-- UPDATE faq.vectorization_status="complete"
  |                    |                |              |<- Updated -|
```

### Scenario 3: Error - Qdrant Unavailable

```
Marcus         Dashboard       Backend        Database    Qdrant      Job Queue
  |               |              |              |           |           |
  |-- Convert FAQ submission    |              |           |           |
  |               |-- PUT /convert-faq ------->|           |           |
  |               |              |-- INSERT faq |-- OK --+           |
  |               |              |-- ENQUEUE task ------>|           |
  |               |              |<- {status: "created, vectorization pending"}
  |               |<- Toast ----<+              |           |           |
  |               |              |              |           |           |
  |               |              |  [Job consumes task] ---|-->         |
  |               |              |              |           |           |
  |               |              |              |           |-- Store vectors
  |               |              |              |           |<- ERROR: timeout
  |               |              |              |           |           |
  |               |              |  [Job fails, queues retry]-------+   |
  |               |              |              |           |       |   |
  |               |              |              |           |       | (retry after 60s)
  |               |              |              |           |       |-->|
  |               |              |              |           |<- Success (Qdrant recovered)
  |               |              |              |           |
  |               |              |-- UPDATE faq.vectorization_status="complete"
  |               |              |              |<- OK ----+
  |               | [Next admin refresh of dashboard]
  |               |-- GET /escalations ------->|
  |               |<- Escalations with FAQ marked "searchable"
```

---

## 7. Deployment View

### Infrastructure

```
Development/Staging/Production Environment:

+-----------------------------------+
| Web Tier                          |
| - Next.js (frontend)              |
| - FastAPI (backend)               |
| - Runs on container/VM            |
+-----------------------------------+
         |
         | Network
         |
+-----------------------------------+
| Data Tier                         |
| - PostgreSQL (RDS or self-managed)|
| - Qdrant (vector DB)              |
| - Redis (job queue)               |
+-----------------------------------+
```

### Environments

| Environment | Purpose | Escalations | Visibility |
|-------------|---------|-------------|-----------|
| Development | Feature development | Test data | Local only |
| Staging | Integration testing | Test data | Team only |
| Production | Live users | Real escalations | Users + admins |

---

## 8. Crosscutting Concepts

### 8.1 Data Model

```
Escalation (new table):
  id: UUID (PK)
  company_id: UUID (FK -> Company, with RLS)
  user_id: UUID (FK -> User)
  original_query: Text (user's unresolved question)
  user_notes: Text (optional context)
  status: Enum (pending | responded | converted | discarded)
  admin_response: Text (optional, if responded)
  created_faq_id: UUID (FK -> FAQ, optional, if converted)
  resolved_by: UUID (FK -> User, optional)
  created_at: Timestamp
  updated_at: Timestamp
  resolved_at: Timestamp (optional)

FAQ (existing table, modified):
  ...existing fields...
  vectorization_status: Enum (pending | complete | failed)
  created_from_escalation_id: UUID (optional, reference back)
```

### 8.2 Security Concept

**Authentication:**
- Existing: JWT token validated on every request
- company_id extracted from token claims
- User identity confirmed

**Authorization (RBAC):**
- Any authenticated user can POST /escalations (create their own)
- Any authenticated user can GET /escalations?user_id={their_id} (view own)
- Admin users only can GET /escalations (all escalations in company)
- Admin users only can PUT /escalations/{id}/* (respond/convert/discard)

**Data Isolation:**
- Application layer: Every query filters by company_id (explicit in ORM)
- Database layer: PostgreSQL RLS policies enforce company_id filtering
- Both layers must pass (defense in depth)

**Encryption:**
- At rest: Database encryption (depends on infrastructure, RDS encryption recommended)
- In transit: HTTPS/TLS 1.3 (standard for all API calls)
- Sensitive fields: user_notes, admin_response encrypted at field level (future improvement, not MVP)

### 8.3 Error Handling

| Scenario | Handling | User Message |
|----------|----------|--------------|
| Escalation creation fails | Return 400/500 with error code | "Error creating escalation. Try again." |
| JWT token expired | Return 401 | Session expired, please log in again |
| User A tries to access User B's escalation | Return 403 Forbidden | Not authorized |
| Qdrant unavailable during FAQ creation | Return 201 (created) + "vectorization pending" | "FAQ created. Searching in 10s." |
| Job queue full | Log warning, continue (eventual retry) | No visible error (admin sees "pending") |

### 8.4 Logging & Monitoring

**Logging:**
- All escalation operations logged: create, update, delete
- Admin user actions logged with timestamp
- Vectorization job successes/failures logged
- Failed job queue entries logged for manual review

**Monitoring:**
- Escalations created per day (gauge)
- Escalations resolved per day (gauge)
- Avg response time: escalation creation (histogram, target <100ms)
- Vectorization job success rate (gauge, target >99%)
- FAQ searchability delay (histogram, target <60s)
- Job queue depth (gauge, alert if >100)

**Alerts:**
- Escalation creation endpoint latency >500ms
- Vectorization job failure rate >1%
- Job queue depth >100 (vectorization backlog)
- Qdrant connectivity issues

---

## 9. Architecture Decisions

| ADR | Title | Status | Decision |
|-----|-------|--------|----------|
| ADR-001 | Multi-Tenancy Data Isolation Strategy | Proposed | Hybrid: App-layer filters PLUS PostgreSQL RLS |
| ADR-002 | Vectorization Failure Handling | Proposed | Async job queue (Celery/RQ) with retry |
| ADR-003 | Confidence Threshold Strategy | Proposed | Dynamic config (default 0.3), tunable at runtime |

---

## 10. Quality Requirements

### Quality Tree

```
OperaBot Escalation System
├── Security
│   ├── Data Isolation (multi-tenant)
│   └── Authorization (RBAC)
├── Reliability
│   ├── Escalation persistence (data not lost)
│   └── Vectorization robustness (FAQ not lost on Qdrant failure)
├── Performance
│   ├── Escalation creation <100ms
│   └── Admin dashboard load <1s
├── Usability
│   ├── Escalation button contextual (only when needed)
│   └── Admin workflow intuitive
└── Scalability
    ├── Support 100+ escalations/day per tenant
    └── Handle concurrent admins (5-10 simultaneously)
```

### Quality Scenarios

| Scenario | Context | Event | Expected Result |
|----------|---------|-------|-----------------|
| Data Isolation | Admin for Company A | Attempts to query escalations | Only sees escalations from Company A |
| Qdrant Failure | Admin converts escalation to FAQ | Qdrant unavailable | FAQ created; vectorization retried automatically |
| High Load | 100 escalations/day | System handles volume | No performance degradation |
| Confidence Calibration | User gets response confidence 0.25 | Escalation button appears | User can escalate |
| Confidence Calibration | User gets response confidence 0.8 | Escalation button hidden | No escalation option |

---

## 11. Risks and Technical Debt

### Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Qdrant failure cascades to FAQ creation | Medium | Medium | Async vectorization (ADR-002); dead-letter queue monitoring |
| RLS policies misconfigured, data leaks between tenants | Low | Critical | Thorough unit testing of RLS; security review before production |
| Confidence threshold too high, escalation fatigue | Medium | Low | Tunable at runtime (ADR-003); monitor escalation_rate daily |
| Confidence threshold too low, users frustrated | Medium | Low | Tunable at runtime (ADR-003); monitor button_clicks metric |
| Job queue infrastructure not available | Low | High | Use RQ (lightweight) for MVP; upgrade to Celery if needed |

### Technical Debt (Acceptable for MVP)

| Item | Description | Remediation Plan |
|------|-------------|------------------|
| Email notifications | Admins not notified of new escalations | Add email service (Sendgrid/SES) after MVP |
| SLA tracking | No visibility into escalation response times | Add SLA monitoring dashboard post-MVP |
| Escalation assignment | All admins see all escalations (no specialization) | Add assignment workflow in next iteration |
| User visibility into escalation status | Users cannot see escalation progress after creation | Add escalation status page for users (future) |
| Vectorization monitoring | Basic logging only, no detailed metrics | Add Prometheus metrics (future) |

---

## 12. Glossary

| Term | Definition |
|------|------------|
| **Escalation** | A failed chat query submitted by a user for admin review |
| **Confidence Score** | RAG system's confidence (0.0-1.0) that response is correct |
| **Vectorization** | Process of converting FAQ text into embeddings for Qdrant |
| **RLS** | Row-Level Security: PostgreSQL feature for tenant isolation |
| **FAQ** | Frequently Asked Question; stored in database and vectorized for RAG |
| **Job Queue** | Background task queue (Celery/RQ) for async work |
| **RBAC** | Role-Based Access Control; admin vs user roles |
| **Multi-Tenant** | Single system serving multiple independent companies |

---

## Appendix: Architectural Decisions Summary

**Key Decisions for MVP:**

1. **Monolith, not microservices**: Escalation system integrates into existing OperaBot monolith
2. **Async vectorization**: FAQ vectorization does not block escalation resolution
3. **Tunable confidence threshold**: Start at 0.3, adjust based on observed escalation rate
4. **Hybrid multi-tenancy enforcement**: Database RLS + application-layer filters
5. **Simple job queue**: Use RQ (not Celery) for initial simplicity; upgrade if needed

**These decisions balance MVP speed with production readiness and can be revisited post-launch based on operational experience.**

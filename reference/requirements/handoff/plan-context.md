# Plan Context: Escalation System MVP

> **Purpose:** Technical context bridge for Claude Code implementation
> **Created by:** Architect
> **Date:** 2026-04-23
> **Status:** Ready for Claude Code review

---

## Technical Stack Summary

**Backend:**
- Language: Python 3.11+
- Framework: FastAPI (existing)
- Database: PostgreSQL 14+ (existing)
- ORM: SQLAlchemy (existing)
- Job Queue: Celery or RQ (new, choose based on existing infrastructure)
- Authentication: JWT via existing auth system

**Frontend:**
- Framework: Next.js 14+ (existing)
- Styling: Tailwind CSS (existing)
- State Management: React hooks (existing pattern)

**Infrastructure:**
- Vector Store: Qdrant (existing, for FAQ vectorization)
- Authentication: JWT token validation
- Deployment: Docker (inferred from current setup)
- Database: PostgreSQL with Row-Level Security enabled

**API & Integration:**
- API Style: REST/JSON (consistent with existing endpoints)
- Authentication: Bearer JWT tokens
- Multi-Tenancy: company_id extracted from JWT claims

---

## Architecture Style & Quality Goals

**Pattern:** Modular Monolith (no microservices)

**Key Quality Goals (Priority Order):**

1. **Security: Multi-Tenant Data Isolation**
   - Escalations isolated by company
   - No data leakage between tenants
   - Validation: Unit tests verify users can only see own company escalations

2. **Reliability: Data Persistence**
   - Escalation data never lost (even if Qdrant fails)
   - FAQ vectorization robust to failures
   - Validation: Job queue handles retries; FAQ marked "pending" until vectors stored

3. **Usability: Contextual Escalation**
   - Escalation button appears only when needed (confidence <0.3)
   - Admin dashboard shows clear escalation status
   - Validation: Escalation button hidden for high-confidence responses

4. **Performance:**
   - Escalation creation <100ms (no vectorization blocking)
   - Admin dashboard load <1s
   - Validation: Performance test suite; monitoring alerts >500ms

5. **Scalability:**
   - Support 100+ escalations/day per tenant
   - Handle concurrent admin operations
   - Validation: Load testing; queue monitoring

---

## Key Architecture Decisions (ADR Summary)

### ADR-001: Multi-Tenancy Data Isolation Strategy

**Decision:** Hybrid approach with both application-layer filters AND PostgreSQL Row-Level Security

**Rationale:**
- Application-layer filters are explicit and auditable
- Database-level RLS provides automatic enforcement as safety net
- Defense in depth protects against developer mistakes
- Industry standard for secure multi-tenant systems

**Implementation:**
- Every query in ORM includes `.filter(escalation.company_id == current_company_id)`
- Alembic migration creates RLS policies on escalations table
- Unit tests verify both layers independently and together
- Security test: User A cannot read User B's escalation even with database access

**Verification:**
- Line of sight: All escalation queries in `app/api/routes/escalations.py` must filter company_id
- RLS policy created in migration `alembic/versions/escalations_table.py`
- Test suite in `tests/integration/test_escalation_isolation.py`

---

### ADR-002: Vectorization Failure Handling for FAQ Conversion

**Decision:** Asynchronous vectorization using job queue (Celery or RQ) with automatic retry

**Rationale:**
- FAQ creation should not wait for Qdrant (non-blocking user experience)
- Job queue provides built-in retry mechanism (up to 3 retries)
- If Qdrant fails, FAQ is created but marked "pending"; retried automatically
- Admin sees transparent status: "FAQ created, vectorization pending"
- Scales well as escalation volume grows

**Implementation:**
- FAQ status field: `vectorization_status` (values: "pending", "complete", "failed")
- Background task: `tasks/vectorization.py` with Celery/RQ task `vectorize_faq(faq_id, company_id)`
- Enqueue task in FEATURE-005 endpoint: `vectorize_faq.delay(faq.id, company_id)`
- Dead-letter queue monitoring for jobs that fail after 3 retries
- Dashboard shows "Searchable" or "Pending (vectorizing)" status

**Verification:**
- Test: FAQ created, Qdrant fails; verify FAQ exists in DB but marked "pending"
- Test: Job queue retries; after Qdrant recovers, FAQ marked "complete"
- Test: Dead-letter monitoring alerts on repeated failures
- Implementation file: `app/tasks/vectorization.py`, `app/api/routes/escalations.py`

---

### ADR-003: Confidence Threshold Strategy for Escalation Availability

**Decision:** Dynamic, tunable threshold (default 0.3) stored in configuration

**Rationale:**
- Based on BA Critical Hypothesis H-05: threshold <30% targets 90% accuracy
- Tunable at runtime without code deployment (ops can adjust)
- Enables A/B testing if needed
- Allows feedback loop: monitor escalation_rate, adjust if needed
- Simple to implement; can upgrade to ML-based later if patterns emerge

**Implementation:**
- Config parameter: `ESCALATION_CONFIDENCE_THRESHOLD` (env var, default 0.3)
- In chat endpoint: `escalation_available = response_confidence < settings.ESCALATION_CONFIDENCE_THRESHOLD`
- Monitoring: Track escalations_created_per_day, escalations_resolved_per_day
- Ops runbook: If escalation_rate too high, increase threshold (e.g., 0.3 -> 0.35)

**Verification:**
- Test: Response confidence 0.2 -> escalation_available = true
- Test: Response confidence 0.8 -> escalation_available = false
- Monitoring dashboard shows escalation volume trends
- Ops can adjust threshold in config and see impact within 5 minutes

---

## Data Model (Core Entities)

**New Table: escalations**

```sql
CREATE TABLE escalations (
  id UUID PRIMARY KEY,
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  original_query TEXT NOT NULL,      -- User's unresolved question
  user_notes TEXT,                   -- Optional context from user
  status VARCHAR(50) NOT NULL,       -- pending | responded | converted | discarded
  admin_response TEXT,               -- Response from admin (if responded)
  created_faq_id UUID REFERENCES faqs(id) ON DELETE SET NULL,
  resolved_by UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  resolved_at TIMESTAMP,
  
  -- RLS Policy
  CONSTRAINT escalation_company_isolation UNIQUE (id, company_id)
);

-- Enable Row-Level Security
ALTER TABLE escalations ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only see escalations from their company
CREATE POLICY escalation_isolation ON escalations
  USING (company_id = current_setting('app.current_company_id')::uuid);
```

**Modified Table: faqs**

Add fields to track escalation origin:

```sql
ALTER TABLE faqs ADD COLUMN vectorization_status VARCHAR(50) DEFAULT 'pending';
ALTER TABLE faqs ADD COLUMN created_from_escalation_id UUID REFERENCES escalations(id);
```

---

## External Integrations

| System | Type | Protocol | Purpose | Notes |
|--------|------|----------|---------|-------|
| Qdrant | Outbound | gRPC or HTTP | Vector storage for FAQ search | Existing integration; reuse FAQ vectorization |
| PostgreSQL | Inbound | psycopg2 | Data persistence | Existing; add RLS policies |
| JWT Auth | Inbound | JWT token | User authentication | Existing; extract company_id from claims |

---

## Performance & Security Requirements

**Performance:**

- Escalation creation endpoint: <100ms (p99)
- Admin escalations list load: <1s (for 100 items)
- FAQ conversion and vectorization: non-blocking (async)
- Vectorization latency target: <10 seconds (FAQ searchable within 10s, usually 2-5s)
- Job queue processing: Consume tasks within 1 minute of enqueue

**Security:**

- Authentication: JWT tokens (existing)
- Authorization: RBAC
  - Any user: can create escalations, view own
  - Admin users: can view all escalations for their company
  - Admin users: can respond, convert, discard
- Data Encryption:
  - At rest: PostgreSQL encryption (depends on infrastructure)
  - In transit: HTTPS/TLS 1.3 (all API calls)
  - Field-level: user_notes and admin_response should be encrypted (future, not MVP)
- Multi-Tenancy: company_id isolation in RLS + application layer

**Compliance:**

- GDPR Art. 17 (Right to be Forgotten): When escalation is deleted, audit log is kept
- Data retention: Escalations retained per company policy (default 1 year, configurable)
- Audit logging: All escalation operations logged with timestamp and user_id

---

## API Endpoints (Summary)

**Chat Endpoint (Modified):**
```
POST /api/chat
Response includes:
{
  "message": "...",
  "confidence": 0.45,
  "escalation_available": true
}
```

**Escalation Endpoints (New):**
```
POST /api/escalations
  - Create new escalation
  - Auth: Any logged-in user
  - Company: Extracted from JWT

GET /api/escalations
  - List escalations
  - Auth: Admin only (for their company)
  - Filters: status, date range, user

GET /api/escalations/{id}
  - View escalation details
  - Auth: User (own escalation) or Admin (any in company)

PUT /api/escalations/{id}/respond
  - Admin responds to escalation
  - Auth: Admin only
  - Body: { admin_response: "..." }
  - Status: pending -> responded

PUT /api/escalations/{id}/convert-faq
  - Convert escalation to FAQ
  - Auth: Admin only
  - Body: { faq_question: "...", faq_answer: "..." }
  - Status: pending -> converted
  - Trigger: Async vectorization task

PUT /api/escalations/{id}/discard
  - Discard escalation without action
  - Auth: Admin only
  - Status: pending -> discarded
```

---

## Frontend Components (Summary)

**User-Facing:**

1. `components/Escalation/EscalationButton.tsx`
   - Conditional render: only if escalation_available=true
   - Click -> opens modal
   - Button text: "📞 Escalar Consulta"

2. `components/Escalation/EscalationModal.tsx`
   - Modal form: user_notes textarea
   - Submit -> POST /api/escalations
   - Success -> toast, modal closes

**Admin-Facing:**

3. `app/(auth)/admin/escalations/page.tsx`
   - List escalations with filters (status, date, user)
   - Row click -> detail panel
   - Actions: Respond, Convert to FAQ, Discard
   - Status indicator: "Vectorization pending..." for converted FAQs

---

## Implementation Phases & Dependencies

**Phase 1: Backend Core (FEATURE-001)**
- Create Escalation model
- Create escalations table + RLS migration
- Create POST /api/escalations endpoint
- Tests: Unit (model), Integration (endpoint)

**Phase 2: Chat Integration (FEATURE-007)**
- Modify chat endpoint to include escalation_available flag
- Add ESCALATION_CONFIDENCE_THRESHOLD config
- Tests: Ensure no regression in chat functionality

**Phase 3: Frontend - User Escalation (FEATURE-002)**
- EscalationButton component
- EscalationModal component
- Integrate into chat UI
- Tests: Component tests, E2E test

**Phase 4: Admin Dashboard - List View (FEATURE-003)**
- GET /api/escalations endpoint
- Admin escalations page
- Filtering, sorting, pagination
- Tests: Integration (endpoint), Component (list)

**Phase 5: Admin Actions (FEATURES-004, 005, 006)**
- PUT /api/escalations/{id}/respond endpoint
- PUT /api/escalations/{id}/convert-faq endpoint (+ async vectorization)
- PUT /api/escalations/{id}/discard endpoint
- Tests: Integration tests for each action

**Phase 6: Async Vectorization (ADR-002)**
- Set up job queue (Celery/RQ)
- Create vectorize_faq task
- Dead-letter queue monitoring
- Tests: Task tests, end-to-end FAQ creation -> searchability

---

## Known Open Questions for Claude Code

**Infrastructure:**
1. Is Celery already set up in OperaBot? If not, use RQ (simpler).
2. Is Redis available for job queue storage?
3. Are there monitoring/alerting systems in place (Prometheus, CloudWatch, etc.)?

**Implementation Details:**
1. How is JWT company_id extracted in existing code? Follow that pattern.
2. What is the existing pattern for FastAPI route organization? Follow it.
3. What testing framework is used? (pytest, unittest?) Follow existing patterns.
4. Are there existing utilities for "get current user" and "get current company"? Reuse them.

**Vectorization:**
1. What is the existing FAQ vectorization code? Reuse for escalation-to-FAQ.
2. How long does embedding generation typically take? Use that for timeout calculations.

---

## Consistency Check: ADRs vs plan-context.md

**Verification (Claude Code must confirm):**

- [ ] ADR-001 (RLS + app filters) implemented in escalations.py queries
- [ ] ADR-002 (async vectorization) implemented via job queue task
- [ ] ADR-003 (confidence threshold) implemented as config + chat endpoint flag
- [ ] All API endpoints match ADR decisions
- [ ] All data model fields present and correct
- [ ] Monitoring metrics match ADR quality goals

---

## Success Criteria for Claude Code

**Implementation is complete when:**

1. All 7 features are implemented (FEATURE-001 through FEATURE-007)
2. All unit tests pass (>90% coverage)
3. All integration tests pass (API endpoints work end-to-end)
4. All ADR decisions implemented correctly
5. No regressions in existing chat or FAQ functionality
6. Admin can complete escalation workflow in <2 minutes
7. Escalations are visible and searchable in admin dashboard

**Verification artifacts:**
- Test results with coverage report
- API endpoint testing (Postman or similar)
- E2E test for complete escalation workflow
- Performance test results (<100ms for escalation creation)

---

## Handoff Checklist for Claude Code

Before starting implementation, verify:

- [ ] Read all ADRs (ADR-001, ADR-002, ADR-003)
- [ ] Read arc42 documentation (Section 5-8 are critical)
- [ ] Read all 7 Feature specifications (FEATURE-001 through FEATURE-007)
- [ ] Understand data model (escalations table + FAQ modifications)
- [ ] Understand API endpoints (CRUD patterns, RBAC)
- [ ] Understand job queue pattern (async vectorization)
- [ ] Understand RLS policies (PostgreSQL-specific)

---

## Documents to Load into Claude Code Context

1. `_devprocess/architecture/ADR-001-escalation-data-isolation.md`
2. `_devprocess/architecture/ADR-002-vectorization-robustness.md`
3. `_devprocess/architecture/ADR-003-confidence-threshold-strategy.md`
4. `_devprocess/architecture/arc42.md` (Sections 1-8 most critical)
5. `_devprocess/requirements/handoff/plan-context.md` (THIS FILE)
6. All FEATURE-*.md files (FEATURE-001 through FEATURE-007)
7. Existing codebase structure (app/api/routes, app/models, etc.)

---

## Next Step: Claude Code

Claude Code will:
1. Load all context documents and ADRs
2. Critically review against real codebase structure
3. Create Issues (ISSUE-*.md) with atomic tasks (1-3 days each)
4. Implement features following TDD approach
5. Run test suite after each change
6. Write back to artifacts as implementation reveals insights
7. Hand off to Developer when ready

**Status: READY FOR CLAUDE CODE REVIEW**

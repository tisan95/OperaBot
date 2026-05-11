# V-MODEL: FROM BUSINESS ANALYSIS TO ARCHITECTURE (COMPLETE)

**Project:** OperaBot - Escalation System MVP
**Status:** Ready for Implementation Phase
**Date:** 2026-04-23

---

## Journey Through the V-Model

```
    EXPLORATION (BA)          IDEATION (BA)         VALIDATION (RE)      ARCHITECTURE
         Phase 1                 Phase 2              Phase 3              Phase 4
         ________                ________            _________            ________

    User + Problem        ->   HMW Question    ->   Epics & Features -> ADRs & Design
    Personas             ->   Value Prop      ->   ASRs & NFRs     ->  Technical Stack
    Needs Analysis       ->   Idea Potential  ->   Success Criteria->  plan-context.md
    Critical Hypotheses  ->   Solution Idea   ->   Traceability    ->  arc42 Docs

    OUTPUT:                 OUTPUT:             OUTPUT:             OUTPUT:
    BA Document             Epics (3)           Features (7)        ADRs (3)
    12 sections             Business Outcomes   User Stories        arc42
    (COMPLETE ✅)           Hypotheses Links    RBAC Spec          plan-context
                            (COMPLETE ✅)       (COMPLETE ✅)      (COMPLETE ✅)
```

---

## Phase 1: EXPLORATION (Business Analyst - COMPLETE ✅)

**Deliverable:** Business Analysis Document (12 sections)

**Discovered:**
- **Problem:** Users with unresolved chat queries have no escalation path
- **Users:** Sarah (frustrated user), Marcus (admin managing knowledge gaps)
- **Needs:**
  - Functional: Submit failed queries for expert review, receive confirmation
  - Emotional: Feel heard when escalating, see progress
  - Social: Know others are helping improve the system
- **Critical Hypotheses:** 5 hypotheses on adoption, accuracy, capability
- **Idea Potential:** Value=8, Transferability=9, Feasibility=8

**Documents Created:**
- ✅ `_devprocess/analysis/BA-{PROJECT}.md` (comprehensive)
- ✅ Personas, needs, insights, trends documented
- ✅ How-Might-We: "How might we help users achieve expert help despite chat limitations?"

---

## Phase 2: IDEATION (Business Analyst - COMPLETE ✅)

**Deliverable:** Value Proposition + Solution Idea + Hypothesis Validation

**Synthesized:**
- **Value Proposition:** "For frustrated users, our escalation system is a one-click escalation mechanism that captures failed queries systematically, unlike manual email workarounds."
- **Solution Idea:**
  - User escalates from chat UI (low-confidence responses)
  - Admin receives escalation, can respond or convert to FAQ
  - New FAQs auto-vectorized and searchable immediately
- **Idea Potential Scores:** All 3 axes >= 8/10 (strong viability)

**Documents Created:**
- ✅ Solution concept documented
- ✅ 5 Critical Hypotheses defined (H-01 through H-05)
- ✅ Mapped to testable criteria

---

## Phase 3: VALIDATION (Requirements Engineer - COMPLETE ✅)

**Deliverable:** Epics & Features with ASRs, NFRs, and Traceability

**Structured Requirements:**

### Epics (3 - Strategic Initiatives)

1. **EPIC-001:** User-Initiated Escalation Workflow
   - Business Outcome: >=80% adoption of escalation button
   - Leading Indicators: >5 escalations week 1, >15 week 2, 20-30/week sustained
   - Features: 3 (FEATURE-001, 002, 007)

2. **EPIC-002:** Admin Escalation Management
   - Business Outcome: 80% resolved <1 day
   - Leading Indicators: 10+ FAQs created from escalations by week 2
   - Features: 4 (FEATURE-003, 004, 005, 006)

3. **EPIC-003:** Chat System Integration
   - Business Outcome: Escalation accuracy >=90%
   - Leading Indicators: <30% confidence correctly flags low-confidence responses
   - Features: 1 (FEATURE-007)

### Features (7 - Functional Capabilities)

| ID | Name | Priority | Epic | ASRs |
|----|------|----------|------|------|
| FEATURE-001 | Escalation Creation Backend | P0 | EPIC-001 | CRITICAL: Multi-tenancy |
| FEATURE-002 | Escalation Button in Chat | P0 | EPIC-001 | None |
| FEATURE-003 | Admin Dashboard | P0 | EPIC-002 | None |
| FEATURE-004 | Admin Response Action | P0 | EPIC-002 | None |
| FEATURE-005 | Convert to FAQ | P0 | EPIC-002 | CRITICAL: Vectorization |
| FEATURE-006 | Discard Escalation | P1 | EPIC-002 | None |
| FEATURE-007 | Confidence Threshold | P0 | EPIC-003 | MODERATE: Threshold Config |

### ASRs Identified

- **CRITICAL:** Multi-Tenancy Enforcement (FEATURE-001)
- **CRITICAL:** Vectorization Robustness (FEATURE-005)
- **MODERATE:** Escalation Persistence (FEATURE-001)

**Documents Created:**
- ✅ `_devprocess/requirements/epics/EPIC-*.md` (3 files)
- ✅ `_devprocess/requirements/features/FEATURE-*.md` (7 files)
- ✅ All features with Jobs to be Done, Acceptance Criteria, NFRs
- ✅ ASRs marked (CRITICAL/MODERATE) for architect

---

## Phase 4: ARCHITECTURE (Architect - COMPLETE ✅)

**Deliverable:** ADRs, arc42 Documentation, plan-context.md

### Architecture Decision Records (3)

**ADR-001: Multi-Tenancy Data Isolation**
- **Triggering ASR:** CRITICAL - Multi-tenancy enforcement
- **Decision:** Hybrid approach (PostgreSQL RLS + application-layer filters)
- **Rationale:** Defense in depth; RLS catches developer mistakes; explicit code is auditable
- **Options Considered:** 3 (Database-only RLS, App-only filters, Hybrid)
- **Consequences:** Slight complexity, small perf overhead, maximum security

**ADR-002: Vectorization Failure Handling**
- **Triggering ASR:** CRITICAL - Escalation persistence & vectorization robustness
- **Decision:** Async job queue (Celery/RQ) with auto-retry
- **Rationale:** Non-blocking UX; built-in retry mechanism; natural failure recovery
- **Options Considered:** 3 (Synchronous blocking, Async queue, Hybrid with timeout)
- **Consequences:** Requires job queue infra, eventual consistency, transparent status

**ADR-003: Confidence Threshold Strategy**
- **Triggering ASR:** MODERATE - Escalation availability tuning
- **Decision:** Dynamic config (default 0.3 from BA hypothesis), tunable at runtime
- **Rationale:** Based on H-05 (threshold <30% targets 90% accuracy); allows feedback loop
- **Options Considered:** 3 (Fixed hardcoded, Dynamic config, ML-based)
- **Consequences:** Requires monitoring; ops must tune; simple to implement

### arc42 Documentation

**Complete 12-section architecture blueprint:**

1. **Introduction & Goals:** 5 quality goals ranked by priority
2. **Constraints:** Tech (PostgreSQL, Qdrant, FastAPI) + Org (MVP scope)
3. **Context & Scope:** C4 system context diagram + interfaces
4. **Solution Strategy:** Tech stack decisions linked to ADRs
5. **Building Blocks:** Component hierarchy (FastAPI routes, schemas, models, services, tasks)
6. **Runtime Views:** Sequence diagrams for 3 critical paths:
   - User escalates failed query
   - Admin converts to FAQ
   - Error handling (Qdrant failure)
7. **Deployment View:** Infrastructure (containers, PostgreSQL, Qdrant, Redis)
8. **Crosscutting Concepts:**
   - Domain Model (escalations table + FAQ modifications)
   - Security (RLS + RBAC + encryption)
   - Error Handling (per-scenario strategies)
   - Logging & Monitoring (metrics, alerts)
9. **Architecture Decisions:** Summary table of all ADRs
10. **Quality Requirements:** Quality tree + testable scenarios
11. **Risks & Technical Debt:** 5 risks with mitigations, tech debt list
12. **Glossary:** 8 key terms defined

### plan-context.md (Developer Handoff)

**Critical context bridge for implementation:**
- Technical Stack (all layers specified)
- Quality Goals (ranked priority 1-5)
- ADR Summary (3 decisions with rationale)
- Data Model (escalations + FAQ schema)
- External Integrations (Qdrant, PostgreSQL, JWT)
- Performance & Security (with numbers)
- API Endpoints (CRUD operations + RBAC)
- Frontend Components (3 new React components)
- Implementation Phases (6 phases with dependencies)
- Open Questions (for Claude Code to resolve)
- Success Criteria (measurable, verifiable)

**Documents Created:**
- ✅ `_devprocess/architecture/ADR-001-escalation-data-isolation.md` (6 KB)
- ✅ `_devprocess/architecture/ADR-002-vectorization-robustness.md` (8 KB)
- ✅ `_devprocess/architecture/ADR-003-confidence-threshold-strategy.md` (7 KB)
- ✅ `_devprocess/architecture/arc42.md` (24 KB)
- ✅ `_devprocess/requirements/handoff/plan-context.md` (15 KB)

---

## Complete Traceability

### Business Outcome -> Feature -> ADR

**BO-001:** 80% escalation adoption
├─ FEATURE-001: Escalation Creation Backend
├─ FEATURE-002: Escalation Button in Chat
├─ FEATURE-007: Confidence-Based Trigger
└─ ADR-003: Confidence Threshold (when to show button)

**BO-002:** 80% escalations resolved <1 day
├─ FEATURE-003: Admin Dashboard (see escalations)
├─ FEATURE-004: Response Action (resolve without FAQ)
└─ ADR-001: Multi-Tenancy (isolate by company)

**BO-003:** FAQ conversion rate 50%
├─ FEATURE-005: Convert to FAQ (with auto-vectorization)
└─ ADR-002: Vectorization Robustness (non-blocking, retry)

### Critical Hypothesis -> Feature -> ADR

**H-01:** Users adopt if confidence <30%
└─ FEATURE-007 validates via escalation_available flag
    └─ ADR-003: Threshold set to 0.3, tunable

**H-02:** Simple modal sufficient for escalation
└─ FEATURE-002 includes EscalationModal component

**H-03:** Admins can convert without data loss
└─ FEATURE-005 with async vectorization
    └─ ADR-002: FAQ created immediately, vectors retry

**H-04:** New FAQ searchable within 5 minutes
└─ FEATURE-005 + ADR-002 async job queue (<10s typical)

**H-05:** Escalation accuracy >=90%
└─ FEATURE-007 with confidence threshold
    └─ ADR-003: Tunable to optimize accuracy

---

## Quality Gates Passed ✅

### BA Document (COMPLETE)
- [x] Problem clearly defined
- [x] At least 2 user personas with needs
- [x] How-Might-We question
- [x] Idea Potential scored on 3 axes (all >=8)
- [x] Value Proposition formulated
- [x] Critical Hypotheses (5) with test methods
- [x] In-Scope/Out-of-Scope explicit

### Requirements Engineering (COMPLETE)
- [x] 3 Epics with Hypothesis Statements
- [x] Business Outcomes quantified (with metrics)
- [x] 7 Features with Benefits Hypothesis
- [x] User Stories (functional/emotional/social) per feature
- [x] Acceptance Criteria (testable, not vague)
- [x] NFRs quantified (response time, throughput, etc.)
- [x] ASRs identified & marked (CRITICAL/MODERATE)
- [x] Dependencies documented

### Architecture (COMPLETE)
- [x] All Critical ASRs have ADRs (3/3)
- [x] Each ADR: MADR format, 3+ options, consequences
- [x] arc42 complete (MVP scope, 12 sections)
- [x] plan-context.md as developer handoff
- [x] Tech stack decisions justified
- [x] Quality goals measurable
- [x] Risk assessment with mitigations
- [x] Traceability complete (BA -> RE -> Architecture)

---

## Next Phase: Implementation (Claude Code)

**Claude Code will:**
1. Load all ADRs, arc42, plan-context.md
2. Review against real OperaBot codebase structure
3. Create Issues (ISSUE-*.md) with atomic tasks
4. Implement features (TDD: tests -> code)
5. Run full test suite (>90% coverage)
6. Update artifacts as needed
7. Hand off to Developer for final implementation

**Estimated Timeline:** 9-11 dev days (1.5-2 weeks)

**Final Deliverables from Claude Code:**
- Issues (ISSUE-*.md): Atomic 1-3 day tasks
- Implementation Plan: Phase breakdown with dependencies
- Test Suite: Unit + Integration + E2E tests
- Updated Artifacts: Reflect actual implementation

---

## Summary Statistics

| Phase | Deliverable | Count | Size |
|-------|-------------|-------|------|
| BA | Business Analysis Document | 1 | ~15 KB |
| RE | Epics | 3 | ~10 KB |
| RE | Features | 7 | ~35 KB |
| Architecture | ADRs (MADR) | 3 | ~21 KB |
| Architecture | arc42 | 1 | 24 KB |
| Architecture | plan-context.md | 1 | 15 KB |
| **Total** | **All Documents** | **16** | **~120 KB** |

**Quality:** All artifacts follow strict quality standards (no vague statements, all numbers specified, decisions justified)

**Status:** Ready for implementation without additional clarification needed

---

## Files Summary

```
OperaBot/
├── _devprocess/
│   ├── analysis/
│   │   └── BA-*.md (Business Analysis)
│   ├── requirements/
│   │   ├── epics/
│   │   │   ├── EPIC-001-user-initiated-escalation.md
│   │   │   ├── EPIC-002-admin-escalation-management.md
│   │   │   └── EPIC-003-chat-integration.md
│   │   ├── features/
│   │   │   ├── FEATURE-001-escalation-creation.md
│   │   │   ├── FEATURE-002-escalation-button.md
│   │   │   ├── FEATURE-003-admin-dashboard.md
│   │   │   ├── FEATURE-004-admin-response.md
│   │   │   ├── FEATURE-005-convert-to-faq.md
│   │   │   ├── FEATURE-006-discard-escalation.md
│   │   │   └── FEATURE-007-confidence-threshold.md
│   │   └── handoff/
│   │       └── plan-context.md (Developer Handoff - CRITICAL)
│   └── architecture/
│       ├── ADR-001-escalation-data-isolation.md
│       ├── ADR-002-vectorization-robustness.md
│       ├── ADR-003-confidence-threshold-strategy.md
│       └── arc42.md (Complete Architecture)
│
├── ARCHITECTURE-READY.md (Phase Completion Summary)
└── V-MODEL-COMPLETION.md (This Document)
```

---

## ✅ Status

**COMPLETE: All phases of Business Analysis, Requirements Engineering, and Architecture Design are finished.**

**READY: Claude Code can begin implementation immediately.**

**NEXT: Implementation Phase (Claude Code creates Issues, implements features, writes tests)**

---

**V-Model Workflow Signature**
Date: 2026-04-23
From: Business Analyst -> Requirements Engineer -> Architect
To: Claude Code (Implementation)
Status: ✅ READY TO PROCEED

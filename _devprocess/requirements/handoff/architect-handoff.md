# Requirements → Architect Handoff

**Project**: OperaBot MVP
**Date**: 2026-04-20
**Scope**: MVP

---

## Purpose

This document summarizes the architectural requirements derived from the OperaBot Business Analysis and the current set of epics and features. It is intended to guide architecture decisions, identify ASRs, and highlight constraints.

---

## Core Capabilities

- Secure user authentication and role-based dashboards.
- Conversational chat assistant that uses company-specific knowledge.
- FAQ knowledge base with search, categories, and document ingestion.
- Analytics for top questions, answer quality, and improvement workflows.

---

## Key NFR Themes

### Performance
- Chat responses should be delivered quickly and reliably.
- Search results should appear in under 2 seconds for common queries.
- Dashboard pages should load within 3 seconds.

### Security
- Multi-tenant data isolation by company.
- Strong authentication and role separation.
- Safe handling of document uploads.

### Scalability
- Support 100+ active users per pilot company.
- Support at least 1,000 FAQs and documents per company.
- Allow company growth with minimal architecture changes.

### Availability
- Auth and knowledge services should be available during business hours.
- Chat and search should maintain operational reliability.

---

## Architecturally Significant Requirements (ASRs)

### CRITICAL ASRs

**ASR #1: Multi-tenant data isolation**
- Why ASR: Data must never leak between companies.
- Quality Attribute: Security
- Impact: Requires tenant-aware data access rules and query filtering.
- Constraint: Use a single database with clear tenant metadata.

**ASR #2: Trustworthy answer generation**
- Why ASR: Operational users must rely on answers for critical tasks.
- Quality Attribute: Reliability
- Impact: Requires retrieval-augmented generation and source attribution.
- Constraint: Use company knowledge as the primary input.

**ASR #3: Fast search and retrieval**
- Why ASR: Users need answers in the moment of action.
- Quality Attribute: Performance
- Impact: Requires indexed search and efficient query execution.
- Constraint: Support 1,000+ docs per company with low latency.

### MODERATE ASRs

**ASR #4: Feedback-driven improvement**
- Why ASR: Knowledge quality depends on usage signals.
- Quality Attribute: Maintainability
- Impact: Requires event capture, analytics, and admin workflows.
- Constraint: Capture answer ratings and repeated questions.

**ASR #5: Secure uploads**
- Why ASR: Document ingestion introduces risk.
- Quality Attribute: Security
- Impact: Requires safe parsing and file validation.
- Constraint: Restrict upload formats and sanitize content.

---

## Open Questions for Architect

- [?] What retrieval layer best balances cost and answer quality for MVP?
- [?] Should we use an external vector store or embedded search engine first?
- [?] What level of role enforcement is required in the backend versus at the UI?
- [?] How should document uploads be validated to prevent malicious content?

---

## Constraints

- Use a single database for MVP with tenant isolation.
- Keep the frontend responsive and accessible on desktop and tablet.
- Use cost-effective LLM options for chat assistance.
- MVP must avoid complex external integrations beyond core SaaS services.

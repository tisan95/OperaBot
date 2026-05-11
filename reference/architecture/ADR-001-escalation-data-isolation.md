# ADR-001: Multi-Tenancy Data Isolation Strategy

**Status:** Proposed
**Date:** 2026-04-23
**Deciders:** Architect, Tech Lead

## Context

OperaBot is a multi-tenant SaaS platform where each Company has its own set of Users, FAQs, Documents, and Chat interactions. The Escalation System introduces a new table (escalations) that must enforce strict company-level data isolation. Failure to enforce isolation could result in data leakage between companies, exposing sensitive user queries.

Current system uses company_id as the tenant identifier, extracted from JWT tokens. All existing models (User, Company, FAQ, Document, ChatMessage) implement company-scoped queries at the database layer.

**Triggering ASR:**
- CRITICAL: Multi-Tenancy Enforcement (FEATURE-001)
- Quality Attribute: Security (Data Confidentiality)

## Decision Drivers

- **Security Requirement**: Users must be completely isolated by company. A user from Company A cannot access escalations from Company B.
- **Data Consistency**: All queries touching escalations must filter by company_id at the database layer, not application layer alone.
- **Scalability**: As escalation volume grows, tenant isolation must not introduce query performance penalties.
- **Operational Risk**: If isolation is broken, it could expose confidential customer queries across tenants.

## Considered Options

### Option 1: Database-Level Row-Level Security (RLS)

Use PostgreSQL Row-Level Security policies to enforce tenant isolation automatically at the database layer. Every SELECT/UPDATE/DELETE on escalations table is filtered by company_id through RLS policies.

```sql
CREATE POLICY escalation_isolation ON escalations
  USING (company_id = current_setting('app.current_company_id')::uuid);
```

- Pro: Enforced at database layer regardless of application logic
- Pro: Protects against accidental query bugs that forget company_id filter
- Pro: Transparent to application code (queries automatically filtered)
- Pro: Industry standard for multi-tenant databases
- Con: Requires PostgreSQL-specific knowledge (not portable to other DBs)
- Con: RLS policies must be carefully maintained alongside schema
- Con: Small performance overhead per query (measurable but acceptable)

### Option 2: Application-Layer Enforcement Only

Every ORM query explicitly includes `.filter(escalation.company_id == user.company_id)`. No database-level policies.

- Pro: Works with any database (no PostgreSQL dependency)
- Pro: Explicit in code (easier to audit visually)
- Con: Developer mistake can accidentally bypass isolation (e.g., forget filter in one query)
- Con: No safety net if ORM layer is bypassed
- Con: Maintenance burden increases with every new query

### Option 3: Hybrid Approach

Application-layer filters (explicit in ORM) PLUS database RLS as a safety net. Both must be satisfied.

- Pro: Defense in depth (two layers of isolation)
- Pro: Application code remains explicit and auditable
- Pro: Database provides automatic enforcement as backup
- Pro: Catches developer mistakes
- Con: Slight complexity (two enforcement points)
- Con: Tiny performance overhead (additive from Options 1 and 2)

## Decision

**Proposed Option:** Option 3 (Hybrid Approach)

**Rationale:**

Multi-tenancy data isolation is a security-critical requirement. A single mistake in the application layer could expose confidential customer data. Option 3 provides defense in depth by enforcing isolation at both the application layer (explicit ORM filters) and the database layer (RLS policies).

Rationale for rejecting Option 1 alone: While RLS is robust, having explicit company_id filters in application code makes isolation visible to developers and auditors. This transparency is valuable for security reviews.

Rationale for rejecting Option 2 alone: The risk of a developer accidentally omitting a company_id filter is unacceptable for a security-critical feature. RLS provides automatic protection against such mistakes.

Option 3 combines the best of both: explicit, auditable code PLUS automatic database-level enforcement.

**Implementation approach:**
1. Add RLS policies to escalations table in Alembic migration
2. In app/api/routes/escalations.py, every query includes explicit company_id filter
3. Document in security.md that both layers are required

## Consequences

### Positive
- Escalations are guaranteed isolated by company even if application code has bugs
- Auditors can inspect code and see explicit company_id filters
- RLS provides automatic catch-all for edge cases
- Security posture is strengthened significantly

### Negative
- Slight complexity in migration code (RLS setup)
- Small performance overhead per query from RLS evaluation
- RLS requires PostgreSQL (not portable to other databases)
- Developers must understand both layers

### Risks
- **Risk: RLS policies conflict with application filters** - Mitigation: Test both layers independently and in combination
- **Risk: RLS policies are misconfigured** - Mitigation: Add test case verifying RLS policy blocks unauthorized queries
- **Risk: JWT extraction of company_id is wrong** - Mitigation: Unit tests verify JWT parsing extracts correct company_id

## Implementation Notes

- Add to Alembic migration that creates escalations table:
  ```sql
  ALTER TABLE escalations ENABLE ROW LEVEL SECURITY;
  CREATE POLICY escalation_isolation ON escalations
    USING (company_id = current_setting('app.current_company_id')::uuid);
  ```
- In backend code: Ensure every query includes `.filter(escalations.c.company_id == current_company_id)`
- Add test: Create escalation as User A (Company A), verify User B (Company B) cannot read it even with database access

## Related Decisions

- ADR-002: Escalation Persistence & Data Integrity (related database concerns)
- FEATURE-001: Escalation Creation Backend (implements this ADR)

## References

- PostgreSQL Row-Level Security: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- OWASP Multi-Tenancy: https://cheatsheetseries.owasp.org/cheatsheets/Multi_Tenant_SaaS_HTML5_Web_Application_Security.html

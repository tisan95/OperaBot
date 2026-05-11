# ADR-002: Database Architecture & Multi-Tenancy Model

**Status**: Accepted  
**Date**: 2026-04-15  
**Author**: Architect  
**Scope**: MVP Data Storage

---

## Context and Problem Statement

OperaBot is a multi-tenant SaaS product. We need to:
- Isolate each company's data completely (security requirement from H-1)
- Support 10-20 companies in MVP (expanding later)
- Scale efficiently (row-level security, not separate databases per tenant)
- Use PostgreSQL (technology stack requirement)

Key questions:
1. **Isolation Strategy**: Separate DB per tenant, shared schema with row-level security (RLS), or shared schema with tenant_id column?
2. **How to enforce isolation**: Application-level filtering, database RLS, or both?
3. **FAQ & document storage**: In relational DB, blob storage, or hybrid?

## Decision Drivers

1. **Security Hypothesis (H-1)**: Companies must be confident their operational knowledge is isolated
2. **Cost**: Shared database + RLS is cheaper than separate DB per tenant
3. **Operational Simplicity**: Single database is easier to backup, patch, and manage than 20+ databases
4. **Scale for Future**: If we grow to 1,000+ customers, separate DB per tenant becomes operational nightmare
5. **Performance**: Modern PostgreSQL RLS is performant enough for MVP-scale queries

## Considered Options

### Option 1: Row-Level Security (RLS) with Shared Schema (CHOSEN)
```
Architecture:
- Single PostgreSQL database for all companies
- Shared schema with tenant_id column on all tables
- PostgreSQL Row-Level Security (RLS) policies enforce isolation
- Application layer adds tenant_id filter as defense-in-depth

Tables structure:
- users (id, email, password_hash, company_id, role)
- faqs (id, company_id, title, content, category, tags, ...)
- documents (id, company_id, filename, extracted_text, ...)
- chats (id, company_id, user_id, messages, ...)
- analytics (id, company_id, question, rating, ...)

Pros:
- Cost-efficient (one DB for all companies)
- Operationally simple (one backup, one patch schedule)
- Scales to 1,000+ companies without infrastructure changes
- PostgreSQL RLS is mature and performant
- Easy to add per-tenant analytics/features later

Cons:
- Requires careful RLS policy configuration (mistakes are security holes)
- RLS adds slight query overhead (but negligible for MVP scale)
- Shared backups mean data from all companies in one backup
```

### Option 2: Separate Database per Tenant
```
Pros:
- Maximum isolation (complete separate database)
- Easier per-tenant customization later

Cons:
- Operational nightmare at 20+ customers (patches, backups, maintenance)
- More expensive (20 DB instances vs. 1)
- Complex deployment/automation (creating DB per customer)
- Doesn't scale beyond a few dozen customers
```

### Option 3: Hybrid: Shared for User Data, Separate for Knowledge Base
```
Pros:
- Compromise between isolation and simplicity

Cons:
- Complexity: split logical schema across two databases
- Hard to manage cross-database queries
- Operational overhead still significant
```

## Decision Outcome

**Choose: Row-Level Security (RLS) with Shared Schema**

**Rationale**:
1. **Cost & Operations**: Single DB is cheapest and easiest to manage for MVP (fits startup operations)
2. **Security via Defense-in-Depth**: RLS + application-layer tenant filtering = strong isolation (better than application-only)
3. **Scales to Future**: If we grow to 100+ companies, RLS-based model continues to work; separate DB model becomes unmaintainable
4. **PostgreSQL RLS Maturity**: PostgreSQL RLS (10.1+) is production-ready and used by many SaaS companies
5. **Hypothesis H-1 Validation**: RLS demonstrates we're serious about data isolation; combined with security audit, builds customer trust

## Consequences

### Good
- Cost-efficient (one database supports all customers)
- Operational simplicity (standard PostgreSQL backup/patch/monitoring)
- Scales naturally as we grow (add more rows, not more databases)
- Defense-in-depth security (RLS + application filtering)

### Bad
- RLS complexity: mistakes can leak data (requires careful code review)
- Single point of failure: if PostgreSQL goes down, all customers are down (but we accept 99.5% uptime, not 100%)
- Careful testing required for RLS policies (security-critical)

### Neutral
- Slight query overhead from RLS (negligible for MVP scale)
- Backup size grows with number of companies (acceptable)

## Implementation Details

### PostgreSQL RLS Policies
```sql
-- Example: Users can only see FAQs from their company
CREATE POLICY faq_isolation ON faqs
  FOR SELECT
  USING (company_id = current_setting('app.current_company_id')::bigint);

-- Admin can only manage their company's data
CREATE POLICY admin_company_isolation ON faqs
  FOR UPDATE, DELETE
  USING (company_id = current_setting('app.current_company_id')::bigint);
```

### Application Layer (FastAPI)
```python
# Each request must set the company_id context
# Middleware extracts company_id from JWT token
# All queries implicitly include: WHERE company_id = current_company_id
```

## Confirmation

This decision is confirmed by:
1. **Security Audit**: Verify RLS policies cover all sensitive tables
2. **Isolation Testing**: Multi-tenant test suite confirms data doesn't leak between companies
3. **Performance Testing**: RLS query overhead <5% of response time budget
4. **Operational Test**: Backup/restore process works with shared schema

## Research Links

- https://www.postgresql.org/docs/current/ddl-rowsecurity.html — PostgreSQL RLS documentation
- https://github.com/ankane/pgsls — Multi-tenant PostgreSQL patterns
- https://www.prisma.io/docs/concepts/components/prisma-schema/relation-mode#multi-tenancy — Prisma multi-tenancy guide
- https://github.com/supertokens/supertokens-core/blob/master/docs/tenants.md — Real-world multi-tenant architecture


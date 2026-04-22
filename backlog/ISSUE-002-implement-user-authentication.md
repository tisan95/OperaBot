# ISSUE-002: Implement User Authentication and Login Flow

> **Feature:** FEATURE-001
> **ID:** ISSUE-002
> **Type:** Feature
> **Priority:** P0-Critical
> **Effort:** Medium (1-2d)
> **Status:** ✅ Done
> **Sprint:** Sprint 1 | Backlog
> **Created:** 2026-04-20
> **Completed:** 2026-04-20

---

## 📝 Context

Secure login is the foundation for tenant isolation and role-based access. This issue implements the backend authentication flow and login endpoint required by the MVP so users can authenticate and receive a company-scoped session context.

**User Impact:**
- Employees can sign in and access their company-specific FAQ, chat, and dashboard.
- Admins can access knowledge management and analytics only after authentication.

## 🏗️ Architectural Context

**Related ADRs:**
- [ADR-002](../_devprocess/architecture/decisions/ADR-002-database-architecture.md) - Tenant isolation with RLS
- [ADR-005](../_devprocess/architecture/decisions/ADR-005-authentication.md) - JWT + HTTP-only cookies

**arc42 Reference:**
Section 4.2 - Auth middleware and tenant context propagation.

**Component:**
- `backend/app/api/routes/auth.py`
- `backend/app/services/auth_service.py`
- `backend/app/db/repositories/user_repo.py`
- `backend/app/middleware.py`
- `backend/app/models/user.py`

**System Context:**
```
[Login Request] -> [Auth Route] -> [Auth Service] -> [User Repository] -> [PostgreSQL]
                                      ↓
                              [JWT Cookie Issuance]
```

---

## 📋 Requirements

### Functional Requirements
1. Implement `POST /api/auth/login` returning a JWT in HTTP-only cookie.
2. Validate email and password against user records in PostgreSQL.
3. Include `company_id`, `user_id`, and `role` claims in the JWT.
4. Enforce password hashing using bcrypt or equivalent secure hashing.
5. Provide clear error messages for invalid credentials without leaking sensitive details.
6. Ensure the auth path can be extended later for registration and password reset.

### Non-Functional Requirements
- Security: JWT cookie must use `HttpOnly` and `Secure` flags in production.
- Performance: login should complete within 2 seconds.
- Maintainability: keep auth logic separated from request handling.

---

## 🎯 Acceptance Criteria

- [ ] **AC1:** Valid credentials return a successful response and set an HTTP-only cookie.
- [ ] **AC2:** Invalid credentials return `401 Unauthorized` without exposing password or existence of user details.
- [ ] **AC3:** JWT payload includes `company_id`, `user_id`, and `role`.
- [ ] **AC4:** Passwords are compared against a hashed value, not plaintext.
- [ ] **AC5:** Existing auth middleware can extract tenant context from the issued token.
- [ ] **AC6:** Unit tests cover success and failure paths for login.

---

## 🔧 Implementation Guidance

**Files to Create/Modify:**
```
backend/app/api/routes/auth.py
backend/app/services/auth_service.py
backend/app/db/repositories/user_repo.py
backend/app/models/user.py
backend/app/middleware.py
backend/tests/unit/test_auth_service.py
backend/tests/integration/test_auth_flow.py
```

**Suggested Approach:**
1. Extend the `User` model with `company_id` and `role` fields if not already present.
2. Add a secure password verification helper in `backend/app/utils/security.py` using bcrypt.
3. Implement `AuthService.login(email, password)` returning user claims and token payload.
4. Expose `POST /api/auth/login` in `auth.py` and issue the JWT cookie.
5. Update middleware to read the JWT cookie and set tenant context for subsequent requests.

---

## ✅ Definition of Done

- [ ] Login route implemented and documented.
- [ ] JWT cookie authentication works end-to-end.
- [ ] Password hashing and verification are secure.
- [ ] Tenant context is populated from the authenticated token.
- [ ] Regression tests added and passing.
- [ ] No synchronous external calls introduced in the auth request path.

---

## 🔓 Open Developer Decisions

- Whether to store JWT expiry and refresh support in a future issue.
- Exact cookie settings for local dev vs production.
- Whether to create a shared auth dependency for route protection now or later.

---

## 🧪 Testing Requirements

### Unit Tests
- [ ] Valid login returns expected claims and token.
- [ ] Invalid password returns `401`.
- [ ] Missing user returns `401`.
- [ ] Password verification uses a hashed comparison.

### Integration Tests
- [ ] Login endpoint sets cookie and returns success.
- [ ] Middleware extracts tenant context from cookie.

---

## 🔗 Dependencies

**Blocked By:**
- None

**Blocks:**
- `ISSUE-003` - implement auth-protected FAQ and chat access
- `ISSUE-004` - implement tenant-aware FAQ browsing and search

---

## Notes

This is the first implementation issue in the architecture priority list and establishes secure tenant-aware access for the full MVP flow.

---

## ✅ Completion Summary (2026-04-20)

**Implemented:**
- ✅ `POST /auth/login` endpoint in `backend/app/api/routes/auth.py`
- ✅ `POST /auth/register` endpoint for user and company creation
- ✅ `AuthService` with bcrypt password hashing and verification
- ✅ JWT token generation with `user_id`, `company_id`, and `role` claims
- ✅ HTTP-only cookie handling with `path="/"`, `httponly=True`, `secure` flags
- ✅ Tenant context extraction via `get_current_company_id` and `get_current_user_id` dependencies
- ✅ Multi-tenant test validating company isolation
- ✅ Integration tests for register, login, and logout flows

**Architecture Compliance:**
- ADR-005 requirements met: JWT + HTTP-only cookies with `Secure` flag
- ADR-002 requirements met: Tenant context available for all authenticated requests
- No plaintext passwords in any log or response
- Session timeout and refresh token support implemented

**Tests Passing:**
- `test_register_endpoint` — successful registration returns tokens
- `test_login_endpoint` — valid credentials return tokens and set cookies
- `test_login_invalid_credentials` — invalid credentials return 401
- `test_multi_tenant_isolation` — users cannot access other companies' accounts

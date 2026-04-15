# ADR-005: Authentication & Authorization Strategy

**Status**: Accepted  
**Date**: 2026-04-15  
**Author**: Architect  
**Scope**: MVP Authentication & Multi-Tenancy

---

## Context and Problem Statement

OperaBot requires secure authentication and authorization:

**Requirements** (from FEATURE-001, FEATURE-003):
- User login with email + password (no SSO in MVP)
- Two roles: User (can access FAQ + chat) and Admin (can manage knowledge)
- Stateless authentication (for horizontal scaling)
- Role-based access control (users can't access admin panel)
- Session timeout after 8 hours of inactivity

**Questions**:
1. JWT vs. session cookies vs. other stateless approach?
2. Where to store tokens (localStorage, cookies)?
3. How to handle token refresh?
4. How to enforce role-based access?

## Decision Drivers

1. **Scalability**: Stateless authentication is required (no shared session store)
2. **Security**: Hypothesis H-1 (companies trust SaaS) requires strong auth
3. **Simplicity**: MVP timeline requires fast implementation
4. **Multi-Tenancy**: Auth must enforce company_id isolation

## Considered Options

### Option 1: JWT with HTTP-Only Cookies (CHOSEN)
```
Strategy:
- Generate JWT token on login (contains user_id, company_id, role)
- Store JWT in HTTP-only cookie (not accessible via JavaScript)
- Refresh token in separate HTTP-only cookie (longer lifetime)
- Use short-lived access token (1 hour)
- Validate JWT signature + expiration on each request

Pros:
- Stateless (no session store needed)
- Secure: HTTP-only cookies prevent XSS attacks
- Standard approach (well-understood, many libraries)
- Works with stateless architecture (FastAPI async)
- Easy to add SSO later (just different token source)

Cons:
- CSRF protection required (but mitigated with SameSite cookie)
- Slightly more complex token refresh flow
```

### Option 2: JWT with localStorage
```
Pros:
- Simple, direct

Cons:
- XSS vulnerable (JavaScript can access token)
- Not suitable for security-critical application
```

### Option 3: Session Cookies + Central Session Store
```
Pros:
- Traditional, simple

Cons:
- Requires shared session store (Redis)
- Not stateless (adds operational complexity)
- Doesn't scale as well
```

## Decision Outcome

**Choose: JWT with HTTP-Only Cookies (Secure, Stateless)**

**Rationale**:
1. **Stateless**: No session store needed (FastAPI + PostgreSQL, no Redis)
2. **Secure**: HTTP-only cookies prevent XSS attacks (addresses security requirements)
3. **Scalable**: Works with horizontal scaling (any server can validate JWT)
4. **Standard**: JWT + cookies is industry-standard for modern web apps
5. **Future-Proof**: Easy to add SSO or OAuth later (just different token source)

## Implementation

### JWT Structure
```json
{
  "user_id": 123,
  "company_id": 456,
  "role": "user",  // or "admin"
  "exp": 1713171000,  // expires in 1 hour
  "iat": 1713167400,
  "jti": "unique-token-id"  // for logout/blacklist
}
```

### Token Lifecycle
```
1. Login: POST /auth/login (email, password)
   - FastAPI validates credentials
   - Generates JWT (1 hour expiration)
   - Returns JWT in HTTP-only cookie "access_token"
   - Also returns refresh token in "refresh_token" cookie (7 days)

2. Authenticated Request: GET /api/faqs
   - Browser sends HTTP-only cookie automatically
   - Middleware extracts JWT from cookie
   - Validates signature + expiration
   - Extracts company_id, role
   - Proceeds to handler

3. Token Expiration:
   - Access token expires after 1 hour
   - Browser attempts request, gets 401
   - Frontend calls POST /auth/refresh with refresh token
   - Backend validates refresh token, issues new access token
   - Request retried with new token

4. Logout: POST /auth/logout
   - Clear cookies on client
   - Optional: Add JWT to blacklist in Redis (for immediate invalidation)
```

### Cookie Configuration
```python
@router.post("/login")
def login(credentials: LoginRequest):
    token = create_jwt_token(user_id, company_id, role)
    
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,      # Prevent JavaScript access
        secure=True,        # HTTPS only
        samesite="lax",     # CSRF protection
        max_age=3600        # 1 hour
    )
    
    return {"message": "Logged in"}
```

### Role-Based Access Control (RBAC)
```python
# FastAPI dependency for auth
async def get_current_user(request: Request) -> User:
    token = request.cookies.get("access_token")
    # Validate + decode JWT
    # Return user with company_id, role
    
# RBAC decorator
def require_admin():
    def decorator(func):
        async def wrapper(current_user: User = Depends(get_current_user)):
            if current_user.role != "admin":
                raise HTTPException(status_code=403, detail="Not authorized")
            return await func(current_user)
        return wrapper
    return decorator

# Usage
@router.post("/admin/faqs")
@require_admin()
async def create_faq(current_user: User):
    # Only admins can reach this
    pass
```

## Consequences

### Good
- Secure: HTTP-only cookies prevent XSS
- Stateless: scales horizontally
- Standard: well-understood pattern
- Strong enforcement of company_id isolation via JWT payload

### Bad
- Requires HTTPS in production (non-negotiable for security)
- Token refresh adds complexity (but standard flow)
- Blacklist/logout requires external storage if immediate invalidation needed (but acceptable for MVP)

### Neutral
- JWT payload is visible (but never contains secrets, only user_id + company_id)

## Confirmation

This decision is confirmed by:
1. **Security Audit**: Verify JWT signature validation, HTTPS-only in production
2. **RBAC Testing**: Verify users cannot access admin endpoints, admins can
3. **Token Refresh Testing**: Verify token refresh flow works (1 hour expiration)
4. **Session Timeout Testing**: Verify logout and session invalidation
5. **XSS Testing**: Verify cookies are HTTP-only (not accessible via JavaScript)

## Research Links

- https://datatracker.ietf.org/doc/html/rfc7519 — JWT (RFC 7519)
- https://fastapi.tiangolo.com/advanced/security/oauth2-jwt/ — FastAPI JWT + OAuth2
- https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html — OWASP JWT best practices
- https://owasp.org/www-community/attacks/csrf — CSRF protection with SameSite cookies


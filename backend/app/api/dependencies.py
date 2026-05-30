"""Dependency injection for FastAPI."""

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.utils.security import decode_token
from app.services.auth_service import AuthService
from app.models.user import User, UserRole
from typing import Optional
import uuid


async def get_current_user_id(request: Request) -> str:
    """Extract user ID from JWT token in Authorization header or cookie.

    Args:
        request: FastAPI request object

    Returns:
        User ID string

    Raises:
        HTTPException: If token missing or invalid
    """
    # Try to get token from Authorization header
    auth_header = request.headers.get("Authorization")
    token = None

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
    else:
        # Try to get from cookies
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
        )

    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return user_id


async def get_current_company_id(request: Request) -> str:
    """Extract company ID from JWT token.

    Args:
        request: FastAPI request object

    Returns:
        Company ID string

    Raises:
        HTTPException: If token missing or invalid
    """
    auth_header = request.headers.get("Authorization")
    token = None

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
    else:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
        )

    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    company_id = payload.get("company_id")
    if not company_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return company_id


async def _get_authenticated_user(request: Request, db: AsyncSession) -> User:
    """Load the full User object for the authenticated request."""
    user_id = await get_current_user_id(request)
    company_id = await get_current_company_id(request)
    result = await db.execute(
        select(User).where(User.id == user_id, User.company_id == company_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def require_super_admin(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency: only super_admin role is allowed."""
    user = await _get_authenticated_user(request, db)
    if user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de Super Admin.",
        )
    return user


async def require_admin(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency: admin and super_admin roles are allowed."""
    user = await _get_authenticated_user(request, db)
    if user.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador.",
        )
    return user

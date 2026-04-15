"""Security utilities: JWT, bcrypt, token management."""

import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional
from app.config import settings


def hash_password(password: str) -> str:
    """Hash password using bcrypt (cost >= 12).

    Args:
        password: Plain text password

    Returns:
        Bcrypt hash string
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash.

    Args:
        password: Plain text password
        password_hash: Bcrypt hash to verify against

    Returns:
        True if password matches hash
    """
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_tokens(
    user_id: str, company_id: str, expires_in_minutes: int = None
) -> dict[str, str]:
    """Create access and refresh tokens.

    Args:
        user_id: User UUID
        company_id: Company UUID
        expires_in_minutes: Optional override for access token expiry

    Returns:
        Dict with access_token and refresh_token
    """
    access_token_expires = timedelta(
        minutes=expires_in_minutes or settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    refresh_token_expires = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    access_token = create_access_token(user_id, company_id, access_token_expires)
    refresh_token = create_refresh_token(user_id, company_id, refresh_token_expires)

    return {"access_token": access_token, "refresh_token": refresh_token}


def create_access_token(
    user_id: str, company_id: str, expires_delta: timedelta
) -> str:
    """Create JWT access token.

    Args:
        user_id: User UUID
        company_id: Company UUID
        expires_delta: Token expiration time

    Returns:
        JWT token string
    """
    to_encode = {
        "sub": user_id,
        "company_id": company_id,
        "type": "access",
        "exp": datetime.utcnow() + expires_delta,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def create_refresh_token(
    user_id: str, company_id: str, expires_delta: timedelta
) -> str:
    """Create JWT refresh token.

    Args:
        user_id: User UUID
        company_id: Company UUID
        expires_delta: Token expiration time

    Returns:
        JWT token string
    """
    to_encode = {
        "sub": user_id,
        "company_id": company_id,
        "type": "refresh",
        "exp": datetime.utcnow() + expires_delta,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def decode_token(token: str) -> Optional[dict]:
    """Decode JWT token.

    Args:
        token: JWT token string

    Returns:
        Token payload dict or None if invalid/expired
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

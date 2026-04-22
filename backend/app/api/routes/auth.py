"""Authentication API routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.api.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
    CurrentUserResponse,
    UserResponse,
    CompanyResponse,
)
from app.api.dependencies import get_current_user_id, get_current_company_id
from app.services.auth_service import AuthService
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest, db: AsyncSession = Depends(get_db)
) -> dict:
    """Register a new user.

    Args:
        request: Registration data
        db: Database session

    Returns:
        AuthResponse with user, company, and tokens

    Raises:
        HTTPException: If registration fails
    """
    try:
        auth_service = AuthService(db)
        result = await auth_service.register(
            request.email, request.password, request.company_name
        )

        # Return response (tokens will be set as HTTP-only cookies separately)
        return result

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)
) -> dict:
    """Login a user.

    Args:
        request: Login credentials
        response: FastAPI response (to set cookies)
        db: Database session

    Returns:
        AuthResponse with user, company, and tokens

    Raises:
        HTTPException: If login fails
    """
    try:
        auth_service = AuthService(db)
        result = await auth_service.login(
            request.email, request.password, request.company_name
        )

        # Set refresh token as HTTP-only cookie
        response.set_cookie(
            key="refresh_token",
            value=result["refresh_token"],
            max_age=7 * 24 * 60 * 60,  # 7 days
            httponly=True,
            secure=settings.APP_ENV == "production",
            samesite="lax",
            path="/",
        )

        # Set access token as HTTP-only cookie
        response.set_cookie(
            key="access_token",
            value=result["access_token"],
            max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            httponly=True,
            secure=settings.APP_ENV == "production",
            samesite="lax",
            path="/",
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {e}",
        )


@router.post("/logout")
async def logout(response: Response) -> dict:
    """Logout a user.

    Args:
        response: FastAPI response (to clear cookies)

    Returns:
        Success message
    """
    response.delete_cookie(key="access_token", secure=settings.APP_ENV == "production", httponly=True, path="/")
    response.delete_cookie(key="refresh_token", secure=settings.APP_ENV == "production", httponly=True, path="/")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=CurrentUserResponse)
async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get current authenticated user.

    Args:
        user_id: User ID from token
        company_id: Company ID from token
        db: Database session

    Returns:
        CurrentUserResponse with user and company

    Raises:
        HTTPException: If user not found
    """
    try:
        auth_service = AuthService(db)
        user = await auth_service.get_current_user(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "role": user.role.value,
                "company_id": str(user.company_id),
            },
            "company": {
                "id": str(user.company.id),
                "name": user.company.name,
            },
        }

    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        # Include real error message for debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}",
        )


@router.post("/refresh")
async def refresh_token(request: Request, response: Response) -> dict:
    """Refresh access token using refresh token.

    Args:
        request: FastAPI request
        response: FastAPI response

    Returns:
        Dict with new access token

    Raises:
        HTTPException: If refresh token invalid
    """
    refresh_token_value = request.cookies.get("refresh_token")

    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token",
        )

    from app.utils.security import decode_token, create_access_token
    from datetime import timedelta

    payload = decode_token(refresh_token_value)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    company_id = payload.get("company_id")

    # Create new access token
    new_access_token = create_access_token(
        user_id,
        company_id,
        timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    # Set new access token as HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.APP_ENV == "production",
        samesite="lax",
        path="/",
    )

    return {"access_token": new_access_token}

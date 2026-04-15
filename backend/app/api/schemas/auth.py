"""Authentication request/response schemas."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class RegisterRequest(BaseModel):
    """User registration request."""

    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")
    company_name: str = Field(..., min_length=1, description="Company name")


class LoginRequest(BaseModel):
    """User login request."""

    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="Password")
    company_name: str = Field(..., description="Company name")


class UserResponse(BaseModel):
    """User response model."""

    id: str
    email: str
    role: str
    company_id: str

    class Config:
        from_attributes = True


class CompanyResponse(BaseModel):
    """Company response model."""

    id: str
    name: str

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Authentication response with tokens."""

    user: UserResponse
    company: CompanyResponse
    access_token: str
    refresh_token: str


class CurrentUserResponse(BaseModel):
    """Current authenticated user response."""

    user: UserResponse
    company: CompanyResponse


class ErrorResponse(BaseModel):
    """Error response."""

    detail: str = Field(..., description="Error message")

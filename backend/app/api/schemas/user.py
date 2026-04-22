"""User schemas for API requests and responses."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.user import UserRole

class UserBase(BaseModel):
    """Campos base que comparten todas las peticiones de usuario."""
    email: EmailStr
    role: UserRole = UserRole.USER
    is_active: bool = True

class UserCreate(UserBase):
    """Esquema para crear un usuario (aquí la contraseña es obligatoria)."""
    password: str = Field(..., min_length=6, description="Mínimo 6 caracteres")

class UserUpdate(BaseModel):
    """Esquema para actualizar: todos los campos son opcionales."""
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    """Lo que el API devuelve al Frontend (filtramos la contraseña)."""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
"""API routes for user management (Admin only)."""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.db.database import get_db
from app.models.user import User, UserRole, UserStatus
from app.api.dependencies import get_current_user_id, get_current_company_id
from app.api.schemas.user import UserResponse, UserCreate, UserUpdate, UserApproveRequest

router = APIRouter(prefix="/users", tags=["users"])
# Configuramos el hash de contraseñas igual que en auth_service
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def _check_admin_permissions(user_id: str, company_id: str, db: AsyncSession):
    """Utilidad interna para asegurar que solo un Admin opere aquí."""
    result = await db.execute(
        select(User).where(User.id == user_id, User.company_id == company_id)
    )
    current_user = result.scalar_one_or_none()
    if not current_user or current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requieren permisos de administrador"
        )

@router.get("/", response_model=List[UserResponse])
async def list_company_users(
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db)
):
    """Obtener lista de todos los usuarios de MI empresa."""
    await _check_admin_permissions(user_id, company_id, db)
    
    result = await db.execute(
        select(User).where(User.company_id == company_id).order_by(User.created_at.desc())
    )
    return result.scalars().all()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_company_user(
    user_in: UserCreate,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db)
):
    """Crear un nuevo empleado dentro de la empresa del Admin."""
    await _check_admin_permissions(user_id, company_id, db)
    
    # Verificamos si el email ya existe para esta compañía
    result = await db.execute(
        select(User).where(User.email == user_in.email, User.company_id == company_id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El email ya existe en esta empresa")

    new_user = User(
        company_id=company_id,
        email=user_in.email,
        password_hash=pwd_context.hash(user_in.password),
        role=user_in.role,
        status=user_in.status or UserStatus.PENDING,
        is_active=user_in.is_active,
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.patch("/{target_id}/approve", response_model=UserResponse)
async def approve_company_user(
    target_id: UUID,
    approval: UserApproveRequest,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
):
    """Approve a pending user and assign role."""
    await _check_admin_permissions(user_id, company_id, db)

    result = await db.execute(
        select(User).where(User.id == target_id, User.company_id == company_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if user.status == UserStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Usuario ya está aprobado")

    user.status = UserStatus.ACTIVE
    user.role = approval.role
    user.is_active = True

    await db.commit()
    await db.refresh(user)
    return user

@router.patch("/{target_id}", response_model=UserResponse)
async def update_company_user(
    target_id: UUID,
    user_in: UserUpdate,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db)
):
    """Modificar datos de un empleado (email, password, rol o estado)."""
    await _check_admin_permissions(user_id, company_id, db)
    
    result = await db.execute(
        select(User).where(User.id == target_id, User.company_id == company_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Seguridad: Un admin no puede bajarse el rango a sí mismo para no quedar bloqueado
    if str(user.id) == user_id and user_in.role == UserRole.USER:
        raise HTTPException(status_code=400, detail="No puedes quitarte el rango de Admin a ti mismo")

    # Actualización selectiva de campos
    if user_in.email: user.email = user_in.email
    if user_in.password: user.password_hash = pwd_context.hash(user_in.password)
    if user_in.role: user.role = user_in.role
    if user_in.status is not None: user.status = user_in.status
    if user_in.is_active is not None: user.is_active = user_in.is_active

    await db.commit()
    await db.refresh(user)
    return user

@router.delete("/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company_user(
    target_id: UUID,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db)
):
    """Eliminar permanentemente un usuario de la empresa."""
    await _check_admin_permissions(user_id, company_id, db)
    
    if str(target_id) == user_id:
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propia cuenta")

    result = await db.execute(
        select(User).where(User.id == target_id, User.company_id == company_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    await db.delete(user)
    await db.commit()
"""User model."""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from app.db.database import Base, GUID


class UserRole(str, PyEnum):
    """User role enumeration."""

    ADMIN = "admin"
    USER = "user"


class User(Base):
    """User model with multi-tenant isolation."""

    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    company_id = Column(GUID(), ForeignKey("companies.id"), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    company = relationship("Company", back_populates="users")

    # Unique email per company (not global)
    __table_args__ = (UniqueConstraint("company_id", "email", name="uq_company_email"),)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, company_id={self.company_id})>"

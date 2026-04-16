"""User repository for data access."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.models.user import User
from typing import Optional
from uuid import UUID


class UserRepository:
    """User data access layer."""

    def __init__(self, db: AsyncSession):
        """Initialize repository.

        Args:
            db: AsyncSession instance
        """
        self.db = db

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID.

        Args:
            user_id: User UUID

        Returns:
            User object or None (with company relationship eagerly loaded)
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id).options(joinedload(User.company))
        )
        return result.scalars().first()

    async def get_by_email(self, company_id: UUID, email: str) -> Optional[User]:
        """Get user by email within a company.

        Args:
            company_id: Company UUID
            email: User email

        Returns:
            User object or None
        """
        result = await self.db.execute(
            select(User).where((User.company_id == company_id) & (User.email == email))
        )
        return result.scalars().first()

    async def get_all_by_company(self, company_id: UUID) -> list[User]:
        """Get all users in a company.

        Args:
            company_id: Company UUID

        Returns:
            List of User objects
        """
        result = await self.db.execute(
            select(User).where(User.company_id == company_id)
        )
        return result.scalars().all()

    async def create(self, user: User) -> User:
        """Create a new user.

        Args:
            user: User object

        Returns:
            Created User object
        """
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user: User) -> User:
        """Update user.

        Args:
            user: User object with updated fields

        Returns:
            Updated User object
        """
        await self.db.merge(user)
        await self.db.commit()
        return user

    async def delete(self, user_id: UUID) -> bool:
        """Delete user by ID.

        Args:
            user_id: User UUID

        Returns:
            True if deleted, False if not found
        """
        user = await self.get_by_id(user_id)
        if not user:
            return False
        await self.db.delete(user)
        await self.db.commit()
        return True

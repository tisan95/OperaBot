"""Authentication business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User, UserRole
from app.models.company import Company
from app.utils.security import hash_password, verify_password, create_tokens
from app.db.repositories.user_repo import UserRepository
from typing import Optional
import re


class AuthService:
    """Authentication and user management service."""

    def __init__(self, db: AsyncSession):
        """Initialize auth service.

        Args:
            db: AsyncSession instance
        """
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(self, email: str, password: str, company_name: str) -> dict:
        """Register new user and company.

        First user for a company becomes admin; subsequent users are regular users.

        Args:
            email: User email
            password: User password
            company_name: Company name (creates if doesn't exist)

        Returns:
            Dict with user, company, and auth tokens

        Raises:
            ValueError: If validation fails
        """
        # Validate email format
        if not self._validate_email(email):
            raise ValueError("Invalid email format")

        # Validate password
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")

        # Check if company exists
        result = await self.db.execute(
            select(Company).where(Company.name == company_name)
        )
        company = result.scalars().first()

        if not company:
            # Create new company
            company = Company(name=company_name)
            self.db.add(company)
            await self.db.flush()

        # Check if email already exists in this company
        existing_user = await self.user_repo.get_by_email(company.id, email)
        if existing_user:
            raise ValueError("Email already registered for this company")

        # Determine role: first user is admin, others are users
        existing_users = await self.user_repo.get_all_by_company(company.id)
        role = UserRole.ADMIN if len(existing_users) == 0 else UserRole.USER

        # Create user
        user = User(
            company_id=company.id,
            email=email,
            password_hash=hash_password(password),
            role=role,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        # Generate tokens
        tokens = create_tokens(str(user.id), str(company.id))

        return {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "role": user.role.value,
                "company_id": str(company.id),
            },
            "company": {"id": str(company.id), "name": company.name},
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
        }

    async def login(
        self, email: str, password: str, company_name: str
    ) -> dict:
        """Login user with email and password.

        Args:
            email: User email
            password: User password
            company_name: Company name (for multi-tenant verification)

        Returns:
            Dict with user, company, and auth tokens

        Raises:
            ValueError: If credentials invalid or company not found
        """
        # Get company
        result = await self.db.execute(
            select(Company).where(Company.name == company_name)
        )
        company = result.scalars().first()
        if not company:
            raise ValueError("Company not found")

        # Get user by email in this company
        user = await self.user_repo.get_by_email(company.id, email)
        if not user:
            raise ValueError("Invalid email or password")

        # Verify password
        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("User account is disabled")

        # Generate tokens
        tokens = create_tokens(str(user.id), str(company.id))

        return {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "role": user.role.value,
                "company_id": str(company.id),
            },
            "company": {"id": str(company.id), "name": company.name},
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
        }

    async def get_current_user(self, user_id: str) -> Optional[User]:
        """Get current authenticated user.

        Args:
            user_id: User UUID from JWT token

        Returns:
            User object or None
        """
        try:
            return await self.user_repo.get_by_id(user_id)
        except Exception:
            return None

    @staticmethod
    def _validate_email(email: str) -> bool:
        """Validate email format.

        Args:
            email: Email string

        Returns:
            True if valid format
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

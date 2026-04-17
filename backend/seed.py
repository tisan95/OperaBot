import asyncio

from sqlalchemy import select

from app.db.database import AsyncSessionLocal, Base, engine
from app.models.company import Company
from app.models.user import User, UserRole
from app.models.chat_message import ChatMessage
from app.utils.security import hash_password

COMPANY_NAME = "OperaBot Demo"
USER_EMAIL = "user@example.com"
USER_PASSWORD = "SecurePass123!"


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(Company).where(Company.name == COMPANY_NAME)
            )
            company = result.scalar_one_or_none()

            if not company:
                company = Company(name=COMPANY_NAME)
                session.add(company)
                await session.flush()
                print(f"Created company: {company.name} ({company.id})")
            else:
                print(f"Company already exists: {company.name} ({company.id})")

            result = await session.execute(
                select(User).where(
                    User.company_id == company.id,
                    User.email == USER_EMAIL,
                )
            )
            user = result.scalar_one_or_none()

            if not user:
                password_hash = hash_password(USER_PASSWORD)
                user = User(
                    company_id=company.id,
                    email=USER_EMAIL,
                    password_hash=password_hash,
                    role=UserRole.ADMIN,
                )
                session.add(user)
                await session.flush()
                print(f"Created admin user: {user.email} ({user.id})")
            else:
                if user.role != UserRole.ADMIN:
                    user.role = UserRole.ADMIN
                    await session.flush()
                    print(f"Updated user to admin: {user.email} ({user.id})")
                else:
                    print(f"Admin user already exists: {user.email} ({user.id})")


if __name__ == "__main__":
    asyncio.run(seed())

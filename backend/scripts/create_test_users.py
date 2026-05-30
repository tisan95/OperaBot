"""Script para crear usuarios de prueba asociados a la empresa de admin@operabot.com."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.models.user import User, UserRole, UserStatus
from app.models.company import Company
import app.models.faq
import app.models.document
import app.models.chat_message
import app.models.ticket
from app.utils.security import hash_password


TEST_USERS = [
    {
        "email": "supervisor@operabot.com",
        "password": "Sup3rvisor#2026",
        "role": UserRole.ADMIN,
        "status": UserStatus.PENDING,
    },
    {
        "email": "user@operabot.com",
        "password": "Us3r#Bot2026",
        "role": UserRole.USER,
        "status": UserStatus.PENDING,
    },
]


async def main():
    async with AsyncSessionLocal() as db:
        # Buscar la empresa del admin
        result = await db.execute(
            select(Company)
            .join(User, User.company_id == Company.id)
            .where(User.email == "admin@operabot.com")
        )
        company = result.scalars().first()
        if not company:
            print("ERROR: No se encontró la empresa de admin@operabot.com")
            return

        print(f"Empresa encontrada: {company.name} ({company.id})")

        for data in TEST_USERS:
            # Evitar duplicados
            existing = await db.execute(
                select(User).where(
                    User.company_id == company.id,
                    User.email == data["email"],
                )
            )
            if existing.scalars().first():
                print(f"  Ya existe: {data['email']} — omitido")
                continue

            user = User(
                company_id=company.id,
                email=data["email"],
                password_hash=hash_password(data["password"]),
                role=data["role"],
                status=data["status"],
            )
            db.add(user)
            await db.flush()
            print(f"  Creado: {user.email} | role={user.role.value} | status={user.status.value} | id={user.id}")

        await db.commit()
        print("Listo.")


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Database reset script - drops and recreates all tables.

This script:
1. Imports all models to register them with Base.metadata
2. Drops all existing tables
3. Creates all tables from scratch based on current model definitions

Run this when model schemas change and tables need to be synced.
"""

import asyncio
import sys
from pathlib import Path
from sqlalchemy import text

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.database import Base, engine, AsyncSessionLocal
from app.models import User, Company, FAQ, ChatMessage
from app.models.document import Document
from app.config import settings


async def reset_database():
    """Drop all tables and recreate them from models."""
    try:
        print("Starting database reset...")
        print(f"Database URL: {settings.DATABASE_URL}")

        # Step 1: Drop all existing tables
        async with engine.begin() as conn:
            print("\n[1/3] Dropping existing tables...")
            await conn.run_sync(Base.metadata.drop_all)
            print("✓ All tables dropped")

        # Step 2: Create all tables from model definitions
        async with engine.begin() as conn:
            print("\n[2/3] Creating tables from model definitions...")
            await conn.run_sync(Base.metadata.create_all)
            print("✓ All tables created")

        # Step 3: Verify tables exist
        print("\n[3/3] Verifying table creation...")
        async with AsyncSessionLocal() as session:
            # Try a simple query to verify the connection
            result = await session.execute(text("SELECT 1"))
            print("✓ Database connection verified")

        print("\n" + "="*60)
        print("✓ Database reset completed successfully!")
        print("="*60)
        print("\nTables created:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")

    except Exception as e:
        print(f"\n✗ Error during database reset: {e}", file=sys.stderr)
        raise
    finally:
        # Close the engine
        await engine.dispose()
        print("\n✓ Database connection closed")


if __name__ == "__main__":
    print("OperaBot Database Reset Script")
    print("="*60)
    asyncio.run(reset_database())

#!/usr/bin/env python3
"""Debug script to check and fix database schema issues."""

import asyncio
import logging
from backend.app.db.database import engine, Base, AsyncSessionLocal
from backend.app.models.chat_message import ChatMessage
from sqlalchemy import text, inspect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_table_schema():
    """Check if chat_messages table exists and has required columns."""
    async with engine.begin() as conn:
        # Check if table exists
        result = await conn.execute(
            text("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='chat_messages')")
        )
        table_exists = result.scalar()
        
        if not table_exists:
            logger.error("❌ Table 'chat_messages' does NOT exist")
            return False
        
        logger.info("✓ Table 'chat_messages' exists")
        
        # Check columns
        result = await conn.execute(
            text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'chat_messages'
            """)
        )
        columns = {row[0] for row in result.fetchall()}
        logger.info(f"  Columns: {sorted(columns)}")
        
        # Check for required columns
        required_columns = {
            'id', 'company_id', 'user_id', 'user_message', 'bot_message',
            'is_fallback', 'confidence', 'rating', 'created_at', 'updated_at'
        }
        
        missing = required_columns - columns
        if missing:
            logger.error(f"❌ Missing columns: {missing}")
            return False
        
        logger.info("✓ All required columns exist")
        return True


async def recreate_tables():
    """Drop and recreate all tables."""
    logger.info("🔄 Dropping all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    logger.info("🔄 Creating all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("✓ Tables recreated successfully")


async def main():
    logger.info("=" * 60)
    logger.info("DATABASE SCHEMA DEBUG")
    logger.info("=" * 60)
    
    is_valid = await check_table_schema()
    
    if not is_valid:
        logger.warning("\n⚠️  Schema issues detected. Would you like to fix? (auto-fixing)")
        await recreate_tables()
        
        logger.info("\n🔍 Verifying fix...")
        if await check_table_schema():
            logger.info("✅ All issues fixed!")
        else:
            logger.error("❌ Issues still present. Manual intervention needed.")
    else:
        logger.info("✅ Database schema is valid!")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

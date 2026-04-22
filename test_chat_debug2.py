#!/usr/bin/env python3
"""Test chat endpoint with detailed debugging - including registration."""

import asyncio
import httpx
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TEST_EMAIL = "debugtest@example.com"
TEST_PASSWORD = "debugpass123"
TEST_COMPANY = "Debug Test Company"
TEST_MESSAGE = "¿Cómo puedo configurar respuestas automáticas?"

async def test_chat():
    """Test chat endpoint with debugging."""
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        try:
            # Step 1: Register
            logger.info("=" * 70)
            logger.info("STEP 1: REGISTER NEW USER")
            logger.info("=" * 70)
            
            register_payload = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "company_name": TEST_COMPANY
            }
            logger.info(f"Registering: {TEST_EMAIL} / {TEST_COMPANY}")
            
            register_response = await client.post(
                "/auth/register",
                json=register_payload
            )
            
            logger.info(f"Register status: {register_response.status_code}")
            if register_response.status_code not in [200, 201]:
                logger.error(f"Register failed: {register_response.text}")
                return
            
            logger.info("✓ User registered successfully")
            
            # Step 2: Login
            logger.info("\n" + "=" * 70)
            logger.info("STEP 2: LOGIN")
            logger.info("=" * 70)
            
            login_payload = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "company_name": TEST_COMPANY
            }
            
            login_response = await client.post(
                "/auth/login",
                json=login_payload
            )
            
            logger.info(f"Login status: {login_response.status_code}")
            if login_response.status_code != 200:
                logger.error(f"Login failed: {login_response.text}")
                return
            
            logger.info("✓ Login successful")
            logger.info(f"Cookies: {dict(login_response.cookies)}")
            
            # Step 3: Send chat message
            logger.info("\n" + "=" * 70)
            logger.info("STEP 3: SEND CHAT MESSAGE")
            logger.info("=" * 70)
            logger.info(f"Message: {TEST_MESSAGE}")
            
            chat_payload = {"message": TEST_MESSAGE}
            
            chat_response = await client.post(
                "/chat/messages",
                json=chat_payload
            )
            
            logger.info(f"Chat status: {chat_response.status_code}")
            logger.info(f"Chat response:\n{chat_response.text}")
            
            if chat_response.status_code == 201:
                logger.info("\n✅ SUCCESS - Chat processed")
                data = chat_response.json()
                logger.info(f"Bot response: {data.get('bot_message', 'N/A')}")
                logger.info(f"Confidence: {data.get('confidence', 0)}")
                logger.info(f"Sources: {len(data.get('sources', []))} found")
            else:
                logger.error(f"\n❌ FAILED - Chat returned {chat_response.status_code}")
        
        except Exception as e:
            logger.error(f"Exception: {type(e).__name__}: {e}", exc_info=True)

if __name__ == "__main__":
    logger.info("\n🔍 CHAT ENDPOINT DEBUG TEST WITH REGISTRATION\n")
    asyncio.run(test_chat())

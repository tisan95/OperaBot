#!/usr/bin/env python3
"""Test chat endpoint with detailed debugging."""

import asyncio
import httpx
import json
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test credentials (change to valid company name if needed)
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpass123"
TEST_COMPANY = "Test Company"
TEST_MESSAGE = "¿Cómo puedo configurar respuestas automáticas?"

async def test_chat():
    """Test chat endpoint with debugging."""
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        try:
            # Step 1: Try to login
            logger.info("=" * 60)
            logger.info("STEP 1: Login")
            logger.info("=" * 60)
            
            login_payload = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "company_name": TEST_COMPANY
            }
            logger.info(f"Sending login request: {json.dumps(login_payload, indent=2)}")
            
            login_response = await client.post(
                "/auth/login",
                json=login_payload
            )
            
            logger.info(f"Login response status: {login_response.status_code}")
            logger.info(f"Login response: {login_response.text}")
            
            if login_response.status_code != 200:
                logger.error(f"Login failed. Cannot proceed with chat test.")
                return
            
            # Step 2: Get auth token from cookies
            logger.info("\n" + "=" * 60)
            logger.info("STEP 2: Extracting auth token")
            logger.info("=" * 60)
            
            cookies = login_response.cookies
            logger.info(f"Cookies received: {dict(cookies)}")
            
            # Step 3: Send chat message
            logger.info("\n" + "=" * 60)
            logger.info("STEP 3: Sending chat message")
            logger.info("=" * 60)
            
            chat_payload = {"message": TEST_MESSAGE}
            logger.info(f"Sending chat request: {json.dumps(chat_payload, indent=2)}")
            
            chat_response = await client.post(
                "/chat/messages",
                json=chat_payload,
                cookies=cookies  # Include auth cookies
            )
            
            logger.info(f"Chat response status: {chat_response.status_code}")
            logger.info(f"Chat response body: {chat_response.text}")
            
            if chat_response.status_code == 201:
                logger.info("\n✅ SUCCESS - Chat message processed")
                response_data = chat_response.json()
                logger.info(f"Response data: {json.dumps(response_data, indent=2)}")
            else:
                logger.error(f"\n❌ FAILED - Status {chat_response.status_code}")
                logger.error(f"Error details: {chat_response.text}")
        
        except Exception as e:
            logger.error(f"Exception occurred: {type(e).__name__}: {e}", exc_info=True)

if __name__ == "__main__":
    print("\n🔍 TESTING CHAT ENDPOINT WITH DEBUGGING")
    print("=" * 60)
    asyncio.run(test_chat())

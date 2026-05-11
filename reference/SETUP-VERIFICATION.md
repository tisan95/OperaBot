# OperaBot Local Setup Verification Checklist

Complete this checklist before starting ISSUE-004 (Chat RAG implementation).

## Infrastructure Setup

- [ ] **Docker Compose running all services**
  ```bash
  docker-compose up -d
  docker ps
  # Should show: postgres, qdrant, ollama containers
  ```

- [ ] **PostgreSQL healthy**
  ```bash
  docker-compose ps db
  # Status should be "Up" with "healthy" check
  curl -s postgresql://santiago:Santi95@localhost:5432/operabot_dev
  ```

- [ ] **Qdrant running on localhost:6333**
  ```bash
  curl http://localhost:6333/health
  # Should return: {"status":"ok"}
  ```

- [ ] **Ollama running on localhost:11434**
  ```bash
  curl http://localhost:11434/api/tags
  # Should return: {"models":[]} or list of models
  ```

## Model Download

- [ ] **Phi-3 model downloaded (for MVP)**
  ```bash
  docker-compose exec ollama ollama list
  # Should show phi-3 in the list
  
  # If missing, pull it:
  docker-compose exec ollama ollama pull phi-3
  ```

- [ ] **Test Phi-3 works**
  ```bash
  curl -X POST http://localhost:11434/api/generate \
    -H "Content-Type: application/json" \
    -d '{
      "model": "phi-3",
      "prompt": "Hello, world!",
      "stream": false
    }'
  # Should get a response within 5 seconds
  ```

## Code Configuration

- [ ] **backend/app/config.py configured for Ollama**
  ```python
  LLM_PROVIDER: str = "ollama"
  LLM_MODEL: str = "phi-3"
  LLM_API_URL: str = "http://localhost:11434/api/generate"
  ```

- [ ] **backend/app/services/llm_client.py supports Ollama**
  - Check `_generate_with_ollama()` function exists
  - Check fallback mechanism is implemented
  - Check timeout is set to 30 seconds

- [ ] **No Gemini/OpenAI API keys in config**
  - Search codebase: `grep -r "GEMINI" backend/`
  - Search codebase: `grep -r "OPENAI" backend/`
  - Should only appear in comments about why NOT using them

## Backend Ready

- [ ] **Backend virtual environment active**
  ```bash
  cd backend
  source venv/bin/activate  # or venv\Scripts\activate (Windows)
  ```

- [ ] **All dependencies installed**
  ```bash
  pip install -r requirements.txt
  ```

- [ ] **Database migrations applied**
  ```bash
  # Check that tables exist
  psql postgresql://santiago:Santi95@localhost:5432/operabot_dev \
    -c "\dt"
  # Should show: users, faqs, chat_messages (if exists)
  ```

- [ ] **Backend starts without errors**
  ```bash
  cd backend
  python -m uvicorn app.main:app --reload
  # Should start on http://localhost:8000
  ```

- [ ] **Test auth endpoint works**
  ```bash
  curl -X POST http://localhost:8000/auth/register \
    -H "Content-Type: application/json" \
    -d '{
      "email": "test@example.com",
      "password": "password123",
      "company_name": "Test Corp"
    }'
  # Should return user and company info
  ```

## Frontend Ready

- [ ] **Frontend dependencies installed**
  ```bash
  cd frontend
  npm install
  ```

- [ ] **Frontend starts without errors**
  ```bash
  npm run dev
  # Should start on http://localhost:3000
  ```

- [ ] **Login page loads**
  ```
  Open http://localhost:3000 in browser
  Should see login form
  ```

## Documentation

- [ ] **OLLAMA-SETUP.md exists** at `docs/OLLAMA-SETUP.md`
  - Explains model switching
  - Explains troubleshooting
  - References Ollama API docs

- [ ] **README.md updated**
  - Mentions "Local LLM with Ollama"
  - Explains "No cloud APIs"
  - Points to OLLAMA-SETUP.md

## Ready for ISSUE-004

Once all checkboxes are complete, you're ready to implement the Chat RAG feature:

1. ✅ Infrastructure is running (PostgreSQL, Qdrant, Ollama)
2. ✅ Backend is configured for Ollama
3. ✅ Models are downloaded (Phi-3)
4. ✅ Auth endpoints working
5. ✅ Frontend loads

**Next:** Implement `backend/app/api/routes/chat.py` with:
- Vector search integration (Qdrant)
- LLM context building (FAQ retrieval)
- Ollama API calls (already wrapped in llm_client.py)
- Chat message storage (PostgreSQL)


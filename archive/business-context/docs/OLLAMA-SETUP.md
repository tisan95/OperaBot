# Ollama Local LLM Setup

## Overview

OperaBot uses **Ollama** for local LLM inference. No cloud APIs (Gemini, OpenAI, etc.) are used.

**Models for MVP:**
- **Phi-3** (3B parameters): Fast (~2-4s on CPU), adequate quality for operational QA
- **Llama3.2** (7-8B parameters): Better quality (~4-6s on CPU), use if Phi-3 isn't good enough

---

## Quick Start

### 1. Ensure Docker Compose is Running
```bash
cd /home/santiago/OperaBot
docker-compose up -d
```

Check that Ollama is running:
```bash
curl http://localhost:11434/api/tags
```

You should see a response like:
```json
{"models": []}
```

### 2. Pull a Model (First Time Only)

If the response shows empty models, pull Phi-3:
```bash
docker-compose exec ollama ollama pull phi-3
```

This downloads the ~1.8GB Phi-3 model (takes 5-10 minutes on good internet).

Check that it downloaded:
```bash
curl http://localhost:11434/api/tags
# Should show {"models": [{"name": "phi-3", ...}]}
```

### 3. Test Ollama is Working

```bash
# Test with a simple prompt
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi-3",
    "prompt": "What is 2+2?",
    "stream": false
  }'
```

You should get a response with the model's answer.

---

## Backend Configuration

The backend is configured to use Ollama:

**File:** `backend/app/config.py`
```python
LLM_PROVIDER: str = "ollama"
LLM_MODEL: str = "phi-3"  # Change to "llama3.2" if needed
LLM_API_URL: str = "http://localhost:11434/api/generate"
LLM_TIMEOUT_SECONDS: int = 30
```

**No API keys needed** (Ollama is local).

---

## Switching Models

### From Phi-3 to Llama3.2 (If Quality Issues)

1. Pull the model:
```bash
docker-compose exec ollama ollama pull llama3.2
```

2. Update config:
```python
# backend/app/config.py
LLM_MODEL: str = "llama3.2"
```

3. Restart backend:
```bash
cd backend
python -m uvicorn app.main:app --reload
```

---

## Troubleshooting

### "Connection refused" error
```
❌ CONNECTION ERROR - Cannot reach Ollama at http://localhost:11434/api/generate
```

**Solution:** Check that Ollama container is running:
```bash
docker ps | grep ollama
```

If not running, start it:
```bash
docker-compose up -d ollama
```

### "Model not found" error
```
❌ OLLAMA ERROR - Status: 404
```

**Solution:** Pull the model:
```bash
docker-compose exec ollama ollama pull phi-3
```

### Slow responses (>5s)
- **CPU-based**: Ollama on CPU is ~3-5s per query. This is normal.
- **GPU available**: To use GPU (faster), edit `docker-compose.yml` and add:
  ```yaml
  ollama:
    runtime: nvidia  # Requires nvidia-docker
```

### Memory issues
- **Phi-3**: Needs ~2GB RAM
- **Llama3.2**: Needs ~4-5GB RAM

If running out of memory, try Phi-3 or reduce context window size in `llm_client.py`.

---

## Architecture

### Chat Flow
```
User Question
    ↓
Chat API (POST /api/chat)
    ↓
Retrieve FAQ context (Qdrant)
    ↓
Build prompt with FAQs
    ↓
Call Ollama (http://localhost:11434)
    ↓
Get response
    ↓
Return to user with sources
```

### Timeout & Fallback
- **Timeout:** 30 seconds (fail fast if Ollama is slow)
- **Fallback:** "Knowledge base unavailable. Please try again."
- **No silent failures:** User is always informed

---

## Performance Expectations

### Phi-3 (MVP Default)
- **CPU only:** ~3-5 seconds per query
- **GPU:** ~1-2 seconds per query
- **Quality:** Adequate for operational QA with RAG
- **Memory:** ~2GB

### Llama3.2 (Quality Upgrade)
- **CPU only:** ~4-6 seconds per query
- **GPU:** ~2-3 seconds per query
- **Quality:** Better reasoning, more detailed answers
- **Memory:** ~4-5GB

---

## Production Deployment

For production, Ollama can run:
1. **On the same server** (current setup, simple)
2. **On a dedicated GPU server** (better performance)
3. **In Kubernetes** (scalable, complex)

For MVP, same-server deployment is fine.

---

## References

- [Ollama GitHub](https://github.com/ollama/ollama)
- [Phi-3 Model Card](https://huggingface.co/microsoft/phi-3)
- [Llama 3.2 Models](https://huggingface.co/meta-llama/Llama-3.2)
- [Ollama REST API Docs](https://github.com/ollama/ollama/blob/main/docs/api.md)


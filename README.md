# OperaBot

Operational knowledge assistant with 100% local AI. No cloud APIs, no external dependencies.

## Stack

- **Backend:** FastAPI + Python 3.11 + SQLAlchemy async
- **Frontend:** Next.js 14+ + React + TypeScript + Tailwind CSS
- **Database:** PostgreSQL (multi-tenant via company_id)
- **Vector DB:** Qdrant (COSINE similarity, 768-dim embeddings)
- **LLM:** Ollama (llama3.2:1b local inference)
- **Embeddings:** Ollama API (nomic-embed-text model)
- **Auth:** JWT tokens in HTTP-only cookies
- **Infrastructure:** Docker Compose (dev), Kubernetes-ready (prod)

## Features

- User registration and login with JWT auth
- Multi-tenant isolation (company-scoped data)
- FAQ knowledge base (create, read, delete)
- Document upload and PDF processing with vectorization
- RAG-powered chat with source attribution and confidence scoring
- Admin analytics dashboard (system metrics and health checks)
- Offline-capable architecture

## Quick Start

### Prerequisites

- Docker & Docker Compose
- PostgreSQL 14+
- Ollama (with llama3.2:1b and nomic-embed-text models)
- Qdrant (vector database)

### Setup

```bash
# Clone repository
git clone https://github.com/your-org/operabot.git
cd operabot

# Start infrastructure
docker compose up -d

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run migrations
python -m alembic upgrade head

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 in your browser.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for system design, decisions, and data model.

## Environment Variables

**Backend** (.env):
```
DATABASE_URL=postgresql://user:password@localhost:5432/operabot_dev
LLM_API_URL=http://localhost:11434/api/generate
LLM_TIMEOUT_SECONDS=300
```

**Frontend** (.env.local):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development

- Backend tests: `pytest` (run from backend/)
- Frontend types: `npm run type-check`
- Build frontend: `npm run build`

## License

MIT
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate (Windows)
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### 2. Start Infrastructure (Docker Compose)
```bash
# From root directory
docker-compose up -d

# Check services are healthy
docker ps
curl http://localhost:6333/health      # Qdrant
curl http://localhost:11434/api/tags   # Ollama
```

### 3. Pull Ollama Model (First Time)
```bash
docker-compose exec ollama ollama pull phi-3
# Takes 5-10 minutes, downloads 1.8GB
```

### 4. Run Backend
```bash
cd backend
python -m uvicorn app.main:app --reload
# Runs on http://localhost:8000
```

### 5. Run Frontend
```bash
cd frontend
npm run dev
# Runs on http://localhost:3000
```

## Architecture

```
[Frontend: Next.js]
         ↓
[Backend: FastAPI]
    ↓          ↓          ↓
[PostgreSQL] [Qdrant]  [Ollama]
  (SQL DB)  (Vectors)  (Local LLM)
```

## Documentation

- [Architecture Decisions (ADRs)](/_devprocess/architecture/decisions/)
- [ARC42 System Design](/_devprocess/architecture/arc42/ARC42-ARCHITECTURE.md)
- [Ollama Local LLM Setup](/docs/OLLAMA-SETUP.md)
- [Development Status](_devprocess/DEVELOPMENT-STATUS.md)
- [Setup Verification](SETUP-VERIFICATION.md)

## Development Status

**Phase 1 (Core Features) - 40% Complete**

- ✅ ISSUE-002: User Authentication (Complete)
- ✅ ISSUE-003: Dashboard & FAQ Browser (Complete)
- 📋 ISSUE-004: Chat Interface with RAG (Next)
- 📋 ISSUE-005+: Admin Panel, Analytics (Planned)

## Testing

### Backend Tests
```bash
cd backend
pytest tests/unit/           # Unit tests
pytest tests/integration/    # Integration tests
pytest                       # All tests
```

### Frontend Tests (Planned)
```bash
cd frontend
npm run test
```

## Running Tests Against All Containers

Make sure all services are running:
```bash
docker-compose up -d
cd backend && pytest && cd ..
cd frontend && npm run test && cd ..
```

## Important Notes

### No Cloud APIs
- **Ollama**: 100% local inference (no Gemini, OpenAI, or Claude APIs)
- **Qdrant**: Self-hosted vector store
- **PostgreSQL**: On-premise database
- All data stays on your infrastructure

### Performance
- Chat response time: <5 seconds on CPU, <2 seconds on GPU
- Authentication: <100ms
- FAQ search: <1 second

### Multi-Tenancy
- Single database, company-level row security
- Users can only access FAQs and chat within their company
- Verified at database and API layers

## Project Structure

```
operabot/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/routes/   # API endpoints
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic (LLM, Auth)
│   │   └── db/           # Database configuration
│   └── tests/
├── frontend/             # Next.js application
│   ├── app/              # App Router pages
│   ├── components/       # React components
│   └── lib/              # Utilities and types
├── _devprocess/          # Architecture and requirements docs
│   ├── architecture/     # ADRs, arc42, handoff docs
│   ├── requirements/     # Epics and features
│   └── context/          # Business analysis
└── docker-compose.yml    # Local dev infrastructure
```

## Contributing

This is an MVP project. Please follow the [architecture decisions](/_devprocess/architecture/decisions/) when adding features.

## License

[Your License Here]

## Support

For setup help, see [SETUP-VERIFICATION.md](SETUP-VERIFICATION.md) and [OLLAMA-SETUP.md](/docs/OLLAMA-SETUP.md).

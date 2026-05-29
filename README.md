# OperaBot

Asistente de conocimiento operativo para empresas (SaaS B2B multi-tenant).
Los empleados preguntan en un chat y el sistema responde usando los documentos 
y FAQs que la empresa ha subido. Solo responde si la similitud supera 0.75 — 
si no, escala automáticamente a un ticket para que el admin lo gestione.

## Stack
- Backend: FastAPI + Python 3.11 + PostgreSQL + SQLAlchemy async
- Frontend: Next.js 14 + TypeScript + Tailwind CSS
- Vector DB: Qdrant (nomic-embed-text, 768 dims, COSINE)
- LLM: Ollama local (llama3.1:8b recomendado)
- Auth: JWT en HTTP-only cookies
- Infra: Docker Compose

## Arrancar en local
```bash
# 1. Infraestructura
docker compose up -d

# 2. Backend
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. Migraciones (primera vez)
cd backend && alembic upgrade head

# 4. Frontend
cd frontend && npm run dev
```

## Estado del MVP
- Auth completo con creación de empresa en registro
- FAQs: CRUD completo con aislamiento por company_id
- Documentos: subida PDF, vectorización, listado y borrado
- Chat RAG: umbral 0.75, fuentes visibles, historial persistido
- Tickets: modelo, endpoints y migración aplicada

## Próximo sprint
1. Conectar chat con tickets cuando no supera umbral
2. Kanban interno para admins
3. Rate limiting y error boundaries

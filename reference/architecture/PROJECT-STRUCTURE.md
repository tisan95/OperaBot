# Project Structure: OperaBot MVP

**Target**: Monorepo structure with clearly separated backend and frontend

---

## Directory Layout

```
operabot/                          # Root repository
├── README.md                       # Project overview
├── .gitignore                      # Git ignore rules
├── .github/
│   ├── workflows/                  # CI/CD pipelines
│   │   ├── test-backend.yml
│   │   ├── test-frontend.yml
│   │   └── deploy.yml
│   └── CODEOWNERS                  # Code ownership
│
├── backend/                        # FastAPI Backend
│   ├── app/
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── config.py               # Configuration (env vars)
│   │   ├── middleware.py           # Auth, tenant context, error handling
│   │   │
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── auth.py         # /auth endpoints (login, logout, register)
│   │   │   │   ├── faqs.py         # /faqs endpoints (CRUD)
│   │   │   │   ├── documents.py    # /documents endpoints (upload, manage)
│   │   │   │   ├── chat.py         # /chat endpoints (Q&A)
│   │   │   │   ├── analytics.py    # /admin/analytics endpoints
│   │   │   │   └── websocket.py    # /ws WebSocket endpoints
│   │   │   │
│   │   │   ├── schemas/
│   │   │   │   ├── auth.py         # Pydantic models for auth
│   │   │   │   ├── faq.py          # FAQ request/response models
│   │   │   │   ├── chat.py         # Chat models
│   │   │   │   ├── analytics.py    # Analytics models
│   │   │   │   └── common.py       # Shared models
│   │   │   │
│   │   │   └── dependencies.py     # Dependency injection (get_current_user, etc.)
│   │   │
│   │   ├── services/
│   │   │   ├── auth_service.py     # Authentication logic
│   │   │   ├── faq_service.py      # FAQ CRUD logic
│   │   │   ├── document_service.py # Document upload + text extraction
│   │   │   ├── chat_service.py     # Chat RAG pipeline
│   │   │   ├── embedding_service.py# Embedding generation
│   │   │   ├── analytics_service.py# Analytics aggregation
│   │   │   ├── kanban_service.py   # Trello integration
│   │   │   └── llm_service.py      # Gemini LLM integration
│   │   │
│   │   ├── models/
│   │   │   ├── user.py             # User SQLAlchemy model
│   │   │   ├── company.py          # Company model
│   │   │   ├── faq.py              # FAQ SQLAlchemy model
│   │   │   ├── document.py         # Document model
│   │   │   ├── chat_history.py     # Chat history model
│   │   │   └── analytics.py        # Analytics aggregation model
│   │   │
│   │   ├── db/
│   │   │   ├── database.py         # SQLAlchemy setup, engine, session factory
│   │   │   ├── repositories/
│   │   │   │   ├── user_repo.py
│   │   │   │   ├── faq_repo.py
│   │   │   │   ├── chat_repo.py
│   │   │   │   └── analytics_repo.py
│   │   │   └── migrations/         # Alembic database migrations
│   │   │       └── versions/
│   │   │
│   │   ├── external/
│   │   │   ├── qdrant_client.py    # Qdrant vector store client
│   │   │   ├── gemini_client.py    # Gemini LLM API client
│   │   │   ├── sentence_transform.py# Embedding model client
│   │   │   └── trello_client.py    # Trello API client
│   │   │
│   │   └── utils/
│   │       ├── security.py         # Password hashing, JWT functions
│   │       ├── logging.py          # Logging setup
│   │       ├── text_processing.py  # Document chunking, text extraction
│   │       └── validators.py       # Common validation functions
│   │
│   ├── tests/
│   │   ├── conftest.py             # Pytest fixtures
│   │   ├── unit/
│   │   │   ├── test_auth_service.py
│   │   │   ├── test_faq_service.py
│   │   │   ├── test_chat_service.py
│   │   │   └── test_embedding_service.py
│   │   ├── integration/
│   │   │   ├── test_auth_flow.py
│   │   │   ├── test_chat_rag.py
│   │   │   └── test_analytics.py
│   │   └── e2e/
│   │       └── test_user_journey.py
│   │
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                  # Docker image for backend
│   ├── pyproject.toml              # Project metadata, black config, pytest config
│   └── .env.example                # Example environment variables
│
├── frontend/                       # Next.js Frontend
│   ├── app/                        # Next.js App Router
│   │   ├── layout.tsx              # Root layout
│   │   ├── page.tsx                # Login page
│   │   │
│   │   ├── (auth)/                 # Protected routes with auth layout
│   │   │   ├── layout.tsx          # Auth wrapper (checks JWT)
│   │   │   │
│   │   │   ├── dashboard/
│   │   │   │   ├── page.tsx        # User dashboard (FAQ + Chat)
│   │   │   │   ├── layout.tsx      # Dashboard layout
│   │   │   │   ├── faq/
│   │   │   │   │   └── page.tsx    # FAQ browser
│   │   │   │   └── chat/
│   │   │   │       └── page.tsx    # Chat interface
│   │   │   │
│   │   │   └── admin/
│   │   │       ├── page.tsx        # Admin dashboard
│   │   │       ├── layout.tsx      # Admin layout
│   │   │       ├── knowledge/
│   │   │       │   ├── page.tsx    # FAQ management
│   │   │       │   └── upload/
│   │   │       │       └── page.tsx# Document upload
│   │   │       ├── analytics/
│   │   │       │   └── page.tsx    # Analytics dashboard
│   │   │       └── settings/
│   │   │           └── page.tsx    # Admin settings
│   │   │
│   │   └── api/                    # API routes (optional, mostly use FastAPI)
│   │       ├── auth/
│   │       │   └── [...].ts        # Proxy auth endpoints (optional)
│   │       └── health.ts           # Health check
│   │
│   ├── components/
│   │   ├── FAQBrowser/
│   │   │   ├── CategoryNav.tsx     # Category navigation
│   │   │   ├── SearchBar.tsx       # FAQ search
│   │   │   ├── ArticleDisplay.tsx  # Article rendering
│   │   │   └── ArticleList.tsx
│   │   │
│   │   ├── Chat/
│   │   │   ├── ChatWindow.tsx      # Main chat container
│   │   │   ├── MessageList.tsx     # Messages display
│   │   │   ├── InputField.tsx      # Message input
│   │   │   ├── AnswerDisplay.tsx   # Answer + sources + confidence
│   │   │   ├── RatingPrompt.tsx    # Helpful/Not helpful
│   │   │   └── EscalationButton.tsx
│   │   │
│   │   ├── AdminDashboard/
│   │   │   ├── AnalyticsOverview.tsx
│   │   │   ├── UnansweredQuestions.tsx
│   │   │   ├── LowRatedAnswers.tsx
│   │   │   ├── TopQuestions.tsx
│   │   │   ├── FAQManager.tsx
│   │   │   ├── DocumentUpload.tsx
│   │   │   └── CreateTaskButton.tsx
│   │   │
│   │   ├── Shared/
│   │   │   ├── Header.tsx
│   │   │   ├── Navigation.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   ├── ErrorBoundary.tsx
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── Card.tsx
│   │   │
│   │   └── Auth/
│   │       ├── LoginForm.tsx
│   │       ├── ProtectedRoute.tsx
│   │       └── AuthProvider.tsx
│   │
│   ├── lib/
│   │   ├── api.ts                  # API client (fetch wrapper)
│   │   ├── auth.ts                 # Auth utilities
│   │   ├── websocket.ts            # WebSocket client
│   │   ├── types.ts                # TypeScript types
│   │   ├── constants.ts            # App constants
│   │   │
│   │   └── hooks/
│   │       ├── useAuth.ts          # Auth hook
│   │       ├── useFetchFAQs.ts     # FAQ data fetching
│   │       ├── useChatWebSocket.ts # Chat WebSocket hook
│   │       ├── useAnalytics.ts     # Analytics data fetching
│   │       └── useForm.ts          # Form handling
│   │
│   ├── styles/
│   │   ├── globals.css             # Tailwind imports + global styles
│   │   └── theme.css               # Custom CSS variables
│   │
│   ├── public/                     # Static assets
│   │   ├── logo.svg
│   │   ├── favicon.ico
│   │   └── images/
│   │
│   ├── tests/
│   │   ├── components/
│   │   │   ├── FAQBrowser.test.tsx
│   │   │   ├── Chat.test.tsx
│   │   │   └── AdminDashboard.test.tsx
│   │   ├── lib/
│   │   │   ├── api.test.ts
│   │   │   └── auth.test.ts
│   │   └── e2e/
│   │       ├── user-journey.test.ts
│   │       └── admin-workflow.test.ts
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── next.config.js
│   ├── Dockerfile                  # Docker image for frontend
│   └── .env.example
│
├── docker-compose.yml              # Local development orchestration
│   # Services: postgres, qdrant, backend, frontend
│
├── kubernetes/                     # Kubernetes manifests (Phase 2)
│   ├── postgres-deployment.yaml
│   ├── qdrant-deployment.yaml
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   └── services.yaml
│
├── _devprocess/                    # Development artifacts
│   ├── context/
│   │   ├── 01_business-analysis.md
│   │   └── 02_requirements.md
│   │
│   ├── requirements/
│   │   ├── epics/
│   │   │   └── EPIC-*.md
│   │   ├── features/
│   │   │   └── FEATURE-*.md
│   │   └── handoff/
│   │       └── architect-handoff.md
│   │
│   └── architecture/
│       ├── decisions/
│       │   ├── ADR-001-backend-framework.md
│       │   ├── ADR-002-database-architecture.md
│       │   ├── ADR-003-vector-store.md
│       │   ├── ADR-004-llm-integration.md
│       │   ├── ADR-005-authentication.md
│       │   ├── ADR-006-frontend-framework.md
│       │   └── ADR-007-rag-pattern.md
│       │
│       ├── arc42/
│       │   └── ARC42-ARCHITECTURE.md
│       │
│       └── diagrams/
│           ├── system-context.png
│           ├── container-diagram.png
│           └── component-diagram.png
│
└── docs/                           # User/admin documentation (Phase 2)
    ├── user-guide.md
    ├── admin-guide.md
    └── api-docs.md
```

---

## Key Structure Decisions

### Backend Structure (FastAPI + SQLAlchemy)

**Service Layer Pattern**:
- Routes only handle HTTP (validation, response formatting)
- Services contain business logic
- Repositories handle data access
- External clients isolated in `external/` folder

**Benefits**:
- Testable (mock services)
- Reusable (services can be called from different routes)
- Clear separation of concerns

### Frontend Structure (Next.js)

**Page-Based Routing**:
- App Router (Next.js 14+) with layout nesting
- Protected routes in `(auth)` group (layout enforces auth)
- Clear separation of user vs. admin sections

**Component Organization**:
- Features grouped in folders (FAQBrowser, Chat, AdminDashboard)
- Shared components in `Shared/`
- Hooks for data fetching and state management

**Benefits**:
- Easy navigation (file structure mirrors URL structure)
- Easy to add new features (create new folder)
- Co-location (component + styles + tests together)

---

## Development Workflow

### Backend Development
```bash
cd backend/
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest              # Run tests
python -m black .   # Format code
uvicorn app.main:app --reload  # Run dev server
```

### Frontend Development
```bash
cd frontend/
npm install
npm run dev         # Dev server at localhost:3000
npm run test        # Run tests
npm run lint        # Run linter
```

### Local Infrastructure (Docker Compose)
```bash
docker-compose up   # Starts: PostgreSQL, Qdrant, Backend, Frontend
# Postgres: localhost:5432
# Qdrant: localhost:6333
# Backend: localhost:8000
# Frontend: localhost:3000
```

---

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@postgres:5432/operabot_dev
QDRANT_HOST=qdrant
QDRANT_PORT=6333
GEMINI_API_KEY=***
JWT_SECRET_KEY=***
JWT_ALGORITHM=HS256
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Testing Strategy

### Backend
- **Unit Tests**: Services + Utils (mock external calls)
- **Integration Tests**: API endpoints + database (use test DB)
- **E2E Tests**: Full user journeys (optional for MVP)

### Frontend
- **Component Tests**: Jest + React Testing Library
- **E2E Tests**: Playwright (optional for MVP)

---

## Dependency Management

### Backend (Python)
```
requirements.txt:
  - FastAPI
  - SQLAlchemy + alembic
  - pydantic
  - python-multipart
  - PyJWT
  - bcrypt
  - qdrant-client
  - google-generativeai
  - sentence-transformers
  - python-docx
  - pypdf
  - requests
  - pytest
  - black, flake8, mypy (dev tools)
```

### Frontend (Node.js)
```
package.json dependencies:
  - next
  - react, react-dom
  - typescript
  - tailwindcss
  - lucide-react (icons)

devDependencies:
  - jest, @testing-library/react
  - eslint, prettier
  - typescript
```

---

**This structure supports rapid development, clear organization, and easy onboarding.**

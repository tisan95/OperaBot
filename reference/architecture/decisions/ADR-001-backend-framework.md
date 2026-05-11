# ADR-001: Backend Framework Selection

**Status**: Accepted  
**Date**: 2026-04-15  
**Author**: Architect  
**Scope**: MVP Backend API

---

## Context and Problem Statement

OperaBot MVP requires a backend API that:
- Handles user authentication and role-based access control
- Manages FAQ articles and document uploads
- Integrates with external LLM APIs for chat Q&A
- Performs semantic search + retrieval via vector database
- Scales to 100+ concurrent requests per company
- Supports multi-tenancy with row-level security

We need to choose a Python web framework that balances:
- **Developer productivity**: Quick iteration for MVP (4-6 months)
- **Performance**: <5 second response time for chat queries
- **Async support**: For concurrent LLM API calls (non-blocking I/O)
- **Ecosystem**: Good libraries for LLM integration, vector search, database access

## Decision Drivers

1. **Technology Stack Constraint**: Python backend is required
2. **Async/Concurrency**: Chat integration requires non-blocking I/O when calling external LLM APIs
3. **ORM Flexibility**: Need both sync and async database access patterns
4. **API Development Speed**: FastAPI is known for rapid API development
5. **Community & Libraries**: Python has strong LLM ecosystem (LangChain, llama-index, OpenAI SDK)

## Considered Options

### Option 1: FastAPI (CHOSEN)
```
Pros:
- Modern, async-first framework (perfect for I/O-heavy operations)
- Automatic OpenAPI/Swagger documentation (great for API clarity)
- Built-in data validation (Pydantic models)
- Very fast performance (benchmarked comparable to Go/Node)
- Excellent async support for LLM API calls
- Large community, good LLM integration libraries
- ASGI compatibility (scalable deployment)

Cons:
- Younger than Django (but mature enough for production)
- Smaller ecosystem than Django (but growing fast)
- Requires explicit async patterns (more to learn)
```

### Option 2: Django + Django REST Framework
```
Pros:
- Battle-tested, huge ecosystem, many packages
- Built-in admin panel, authentication, ORM
- Mature and well-documented

Cons:
- Synchronous-first (requires celery/channels for async work)
- Heavier framework (more boilerplate for simple APIs)
- Slower development for simple CRUD APIs compared to FastAPI
- ORM more coupled to Django (harder to reuse in other contexts)
```

### Option 3: Flask
```
Pros:
- Lightweight, minimal
- Easy to learn

Cons:
- Too minimal for complexity of OperaBot
- Would need to assemble many libraries (auth, validation, async)
- Slower development overall
```

## Decision Outcome

**Choose: FastAPI**

**Rationale**:
1. **Async is Critical**: Chat feature requires non-blocking LLM API calls. FastAPI's async support is native and elegant, avoiding callback hell or complex celery setup.
2. **Rapid Development**: Pydantic models, automatic documentation, built-in validation reduce boilerplate. Important for MVP timeline.
3. **Performance**: FastAPI benchmarks show performance equivalent to Go/Node frameworks, meeting <5 sec chat response requirement.
4. **LLM Ecosystem**: Python's LLM libraries (LangChain, llama-index, OpenAI SDK) integrate seamlessly with FastAPI async patterns.
5. **Proven for This Use Case**: Many LLM-powered products (e.g., chatbot services) are built on FastAPI.

## Consequences

### Good
- Fast iteration cycle (MVPs ship faster with FastAPI)
- Clean async code for LLM integration
- Auto-generated API docs (Swagger/OpenAPI) help frontend developers
- SQLAlchemy async support pairs well with FastAPI

### Bad
- Team must learn FastAPI patterns (if coming from Django background)
- Fewer "batteries included" vs. Django (but this is okay for focused MVP)
- Less community guidance for some edge cases (but ecosystem is growing)

### Neutral
- Deployment is ASGI-based (requires Uvicorn, Gunicorn with ASGI worker) — this is standard practice

## Confirmation

This decision is confirmed by:
1. **Performance Testing**: Benchmark FastAPI response time with async LLM calls to ensure <5 sec target
2. **Integration Testing**: Verify SQLAlchemy async integration works well
3. **Team Feedback**: Ensure team is comfortable with async Python patterns

## Research Links

- https://fastapi.tiangolo.com/ — Official FastAPI docs
- https://fastapi.tiangolo.com/#performance — Performance benchmarks
- https://fastapi.tiangolo.com/advanced/async-sql-databases/ — Async database patterns
- https://python-asyncio.readthedocs.io/ — Python asyncio reference
- https://github.com/tiangolo/fastapi/tree/master/docs/src/async_sql_databases — FastAPI + SQLAlchemy async example


# Technology Stack

## Backend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | FastAPI | 0.104+ | REST API server |
| Language | Python | 3.11+ | Server-side logic |
| Database | PostgreSQL | 14+ | User, FAQ, Document data |
| ORM | SQLAlchemy | 2.0+ | Async database access |
| Validation | Pydantic | 2.0+ | Request/response schemas |
| Auth | JWT | - | Token-based authentication |
| Hashing | bcrypt | - | Password hashing (cost 12) |
| PDF Processing | PyPDF2 | - | Extract text from documents |
| Async | asyncio | - | Non-blocking I/O |

## Frontend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | Next.js | 14+ | React framework with routing |
| Language | TypeScript | 5.0+ | Type-safe JavaScript |
| Styling | Tailwind CSS | 3.0+ | Utility-first CSS |
| State | React Context | - | Auth state management |
| API Client | Fetch API | - | HTTP requests with auth |
| Package Manager | npm | 10+ | Dependency management |

## Data & AI
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Vector DB | Qdrant | 1.7+ | Vector search (COSINE, 768-dim) |
| LLM | Ollama | Latest | Local inference (llama3.2:1b) |
| Embeddings | Ollama | Latest | Text to 768-dim vectors (nomic-embed-text) |
| Vector Library | qdrant-client | 2.0+ | Python SDK for Qdrant |
| HTTP Client | httpx | 0.24+ | Async HTTP for Ollama API |

## Infrastructure
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Containers | Docker | Package services |
| Orchestration | Docker Compose | Local development setup |
| CI/CD | GitHub Actions | Automated testing (optional) |
| Tests | pytest | Backend unit/integration tests |
| Linting | flake8/black | Code quality |

## Zero External APIs
- ✅ No OpenAI, Anthropic, or cloud LLMs
- ✅ No cloud vector databases (Pinecone, Weaviate, etc.)
- ✅ No external authentication services
- ✅ No CDN or object storage (everything local)

## Environment Requirements
- **CPU:** 4+ cores recommended
- **RAM:** 8GB minimum, 16GB recommended (Ollama + services)
- **Disk:** 20GB+ (models + database)
- **GPU:** Optional (CPU works fine for small models like llama3.2:1b)

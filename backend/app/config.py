"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/operabot_dev"

    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # App
    APP_ENV: str = "development"
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    # LLM Configuration (Local Ollama - No Cloud APIs)
    LLM_PROVIDER: str = "ollama"  # Local LLM provider
    LLM_MODEL: str = "llama3.2:1b"  # Llama 3.2 1B model for local inference
    LLM_API_URL: str = "http://localhost:11434/api/generate"  # Ollama local endpoint
    LLM_TIMEOUT_SECONDS: int = 300  # Allow up to 5 minutes for LLM generation
    
    QDRANT_URL: str = "http://localhost:6333"

    # File storage — PDFs uploaded by admins
    DOCUMENTS_STORAGE_PATH: str = "./uploads/documents"

    # API key — required for groq and anthropic providers, unused for ollama
    LLM_API_KEY: str | None = None

    # Provider-specific defaults (overridden per provider when LLM_PROVIDER changes)
    GROQ_API_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    ANTHROPIC_API_URL: str = "https://api.anthropic.com/v1/messages"
    ANTHROPIC_VERSION: str = "2023-06-01"

    # Legacy alias, kept for any existing .env files
    GEMINI_API_KEY: str | None = None

    # Configuración de Pydantic v2
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Esto evita que el server pete si hay variables extra en el .env
    )

    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse ALLOWED_ORIGINS string into list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
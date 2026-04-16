"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.config import settings
from app.utils.logging import setup_logging
from app.middleware import setup_middleware
from app.db.database import init_db, close_db
from app.api.routes import auth
from app.api.routes.faq import router as faq_router
from app.api.routes.chat import router as chat_router
import app.models.faq


# Setup logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events.

    Args:
        app: FastAPI application
    """
    # Startup
    await init_db()
    print("✓ Database initialized")
    yield
    # Shutdown
    await close_db()
    print("✓ Database connection closed")


# Create FastAPI app
app = FastAPI(
    title="OperaBot API",
    description="Operational Knowledge Assistant API",
    version="0.1.0",
    lifespan=lifespan,
)

# Setup middleware
setup_middleware(app)

# Include routers
app.include_router(auth.router)
app.include_router(faq_router)
app.include_router(chat_router)


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Health check endpoint.

    Returns:
        Health status
    """
    return {"status": "healthy", "version": "0.1.0"}


# Root endpoint
@app.get("/", tags=["root"])
async def root() -> dict:
    """Root endpoint.

    Returns:
        Welcome message
    """
    return {
        "message": "OperaBot API",
        "version": "0.1.0",
        "docs": "/docs",
    }


# Exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )

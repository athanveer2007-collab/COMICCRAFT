"""Main FastAPI application entrypoint."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1.routes_comics import router as comics_router
from app.api.v1.routes_dev import router as dev_router
from app.api.v1.routes_health import router as health_router
from app.core.config import settings
from app.core.errors import register_error_handlers
from app.core.logging import configure_logging, get_logger
from app.core.security import setup_security_and_cors
from app.db.database import init_db

# Configure logging on startup
configure_logging(settings.LOG_LEVEL)
logger = get_logger("comiccraft.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    logger.info(f"Starting ComicCraft Backend in [{settings.ENVIRONMENT}] environment")
    # Ensure storage paths exist
    _ = settings.images_storage_path
    _ = settings.pdfs_storage_path
    # Initialize database tables
    await init_db()
    yield
    logger.info("Shutting down ComicCraft Backend")


def create_app() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title="ComicCraft API",
        description="Production-grade AI Comic Generator API",
        version="0.1.0",
        openapi_url="/api/v1/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Middleware & Security
    setup_security_and_cors(app)

    # Global Exception Handlers
    register_error_handlers(app)

    # Mount API v1 Routers
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(comics_router, prefix="/api/v1")
    app.include_router(dev_router, prefix="/api/v1")

    # Static file serving for generated images and PDFs
    storage_path = settings.storage_path
    storage_path.mkdir(parents=True, exist_ok=True)
    app.mount("/storage", StaticFiles(directory=str(storage_path)), name="storage")

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
    )

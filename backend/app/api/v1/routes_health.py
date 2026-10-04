"""Health check endpoint."""

import os

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def check_health() -> HealthResponse:
    """Verify health status of ComicCraft backend service."""
    # Check storage writability
    storage_writable = False
    try:
        storage_path = settings.storage_path
        storage_path.mkdir(parents=True, exist_ok=True)
        test_file = storage_path / f".health_check_{os.getpid()}"
        test_file.write_text("ok")
        if test_file.exists():
            test_file.unlink()
            storage_writable = True
    except Exception:
        storage_writable = False

    return HealthResponse(
        status="ok",
        version="0.1.0",
        environment=settings.ENVIRONMENT,
        storage_writable=storage_writable,
    )

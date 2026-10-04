"""REST and Server-Sent Events endpoints for Comics."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.comic import (
    ComicCreateRequest,
    ComicRegenerateRequest,
    ComicResponse,
)
from app.schemas.job import JobCreateResponse
from app.services.comic_service import ComicService
from app.services.job_service import broadcaster

router = APIRouter(prefix="/comics", tags=["Comics"])


@router.post("", response_model=JobCreateResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_comic(
    request: ComicCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JobCreateResponse:
    """Create and trigger asynchronous generation of a 5-panel comic."""
    service = ComicService(db)
    return await service.create_comic(request)


@router.get("/{comic_id}", response_model=ComicResponse)
async def get_comic(
    comic_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ComicResponse:
    """Retrieve full comic with all 5 panels, narration, dialogue, and image assets."""
    service = ComicService(db)
    return await service.get_comic(comic_id)


@router.get("/{comic_id}/events")
async def get_comic_events(comic_id: str) -> StreamingResponse:
    """Real-time Server-Sent Events (SSE) stream broadcasting generation progress."""
    return StreamingResponse(
        broadcaster.subscribe(comic_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post(
    "/{comic_id}/regenerate", response_model=JobCreateResponse, status_code=status.HTTP_202_ACCEPTED
)
async def regenerate_comic(
    comic_id: str,
    request: ComicRegenerateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JobCreateResponse:
    """Regenerate comic narrative and artwork using updated tone and/or art style."""
    service = ComicService(db)
    return await service.regenerate_comic(comic_id, request)

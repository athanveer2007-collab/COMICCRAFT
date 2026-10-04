"""REST and Server-Sent Events endpoints for Comics, including PDF export and download."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import NotFoundException
from app.db.database import get_db
from app.export import pdf_exporter
from app.schemas.comic import (
    ComicCreateRequest,
    ComicRegenerateRequest,
    ComicResponse,
)
from app.schemas.job import JobCreateResponse
from app.services.comic_service import ComicService
from app.services.job_service import broadcaster

router = APIRouter(prefix="/comics", tags=["Comics"])


class PDFExportResponse(BaseModel):
    """Response returning downloadable PDF endpoint."""

    pdf_url: str
    message: str


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


@router.post("/{comic_id}/export", response_model=PDFExportResponse)
async def export_comic_pdf(
    comic_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PDFExportResponse:
    """Trigger or refresh PDF compilation for a completed comic."""
    service = ComicService(db)
    comic = await service.comic_repo.get_by_id(comic_id)
    if not comic:
        raise NotFoundException("Comic", comic_id)

    if not comic.panels or comic.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot export PDF: Comic generation is not yet completed.",
        )

    comic_img_dir = settings.images_storage_path / comic_id
    pdf_path = pdf_exporter.generate_pdf(
        comic_id=comic_id,
        title=comic.title or "ComicCraft Story",
        character_name=comic.character_name,
        setting=comic.custom_setting or comic.setting,
        tone=comic.tone,
        art_style=comic.art_style,
        synopsis=comic.synopsis or "",
        panels=comic.panels,
        image_dir=comic_img_dir,
    )

    await service.comic_repo.update(comic_id, pdf_path=str(pdf_path))

    return PDFExportResponse(
        pdf_url=f"/api/v1/comics/{comic_id}/pdf",
        message="PDF export compiled successfully.",
    )


@router.get("/{comic_id}/pdf")
async def download_comic_pdf(
    comic_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> FileResponse:
    """Download the generated PDF as a file attachment."""
    service = ComicService(db)
    comic = await service.comic_repo.get_by_id(comic_id)
    if not comic:
        raise NotFoundException("Comic", comic_id)

    if not comic.pdf_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF has not been generated for this comic yet. Please call /export first.",
        )

    file_path = Path(comic.pdf_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file is missing on storage server.",
        )

    download_filename = f"comiccraft_{comic.character_name.lower()}_{comic_id[:8]}.pdf"
    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=download_filename,
    )

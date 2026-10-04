"""High-level application service for comic creation, retrieval, and regeneration."""

import asyncio
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundException, ValidationException
from app.db.repositories import ComicRepository, JobRepository
from app.schemas.comic import (
    ComicCreateRequest,
    ComicRegenerateRequest,
    ComicResponse,
    PanelResponse,
)
from app.schemas.job import JobCreateResponse
from app.services.generation_service import generation_service


class ComicService:
    """Application service for comic entities."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.comic_repo = ComicRepository(session)
        self.job_repo = JobRepository(session)

    async def create_comic(self, request: ComicCreateRequest) -> JobCreateResponse:
        """Create new comic and job, then dispatch background generation pipeline."""
        comic_id = str(uuid.uuid4())
        job_id = str(uuid.uuid4())

        # Validate custom setting requirement
        if request.setting.lower() == "custom setting" and not request.custom_setting:
            raise ValidationException(
                "Custom setting description is required when 'Custom setting' is selected."
            )

        # Persist comic record
        _ = await self.comic_repo.create(
            comic_id=comic_id,
            prompt=request.prompt,
            character_name=request.character_name,
            setting=request.setting,
            custom_setting=request.custom_setting,
            tone=request.tone,
            art_style=request.art_style,
        )

        # Persist job record
        _ = await self.job_repo.create(job_id=job_id, comic_id=comic_id)

        # Dispatch async task without blocking HTTP request
        asyncio.create_task(generation_service.run_pipeline(comic_id=comic_id, job_id=job_id))

        return JobCreateResponse(
            job_id=job_id,
            comic_id=comic_id,
            status="in_progress",
            stage="queued",
        )

    async def get_comic(self, comic_id: str) -> ComicResponse:
        """Fetch full comic with all panel details."""
        comic = await self.comic_repo.get_by_id(comic_id)
        if not comic:
            raise NotFoundException("Comic", comic_id)

        # Format panels
        panels_data = None
        if comic.panels:
            panels_data = [PanelResponse.model_validate(p) for p in comic.panels]

        pdf_url = f"/api/v1/comics/{comic_id}/pdf" if comic.pdf_path else None

        return ComicResponse(
            id=comic.id,
            prompt=comic.prompt,
            character_name=comic.character_name,
            setting=comic.setting,
            custom_setting=comic.custom_setting,
            tone=comic.tone,
            art_style=comic.art_style,
            title=comic.title,
            synopsis=comic.synopsis,
            character_sheet=comic.character_sheet,  # type: ignore[arg-type]
            status=comic.status,
            panels=panels_data,
            pdf_path=comic.pdf_path,
            pdf_url=pdf_url,
            error_code=comic.error_code,
            error_message=comic.error_message,
            created_at=comic.created_at,
            updated_at=comic.updated_at,
        )

    async def regenerate_comic(
        self,
        comic_id: str,
        request: ComicRegenerateRequest,
    ) -> JobCreateResponse:
        """Regenerate comic with updated tone and/or art style."""
        comic = await self.comic_repo.get_by_id(comic_id)
        if not comic:
            raise NotFoundException("Comic", comic_id)

        # Update comic attributes
        new_tone = request.tone or comic.tone
        new_style = request.art_style or comic.art_style

        await self.comic_repo.update(
            comic_id,
            tone=new_tone,
            art_style=new_style,
            status="queued",
            error_code=None,
            error_message=None,
        )

        job_id = str(uuid.uuid4())
        _ = await self.job_repo.create(job_id=job_id, comic_id=comic_id)

        # Launch regeneration pipeline
        asyncio.create_task(generation_service.run_pipeline(comic_id=comic_id, job_id=job_id))

        return JobCreateResponse(
            job_id=job_id,
            comic_id=comic_id,
            status="in_progress",
            stage="queued",
        )

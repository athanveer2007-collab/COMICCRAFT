"""Database repositories for Comics and Jobs."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ComicModel, JobModel


class ComicRepository:
    """Repository handling CRUD operations for comics."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, comic_id: str) -> ComicModel | None:
        """Fetch comic by ID."""
        stmt = select(ComicModel).where(ComicModel.id == comic_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        comic_id: str,
        prompt: str,
        character_name: str,
        setting: str,
        tone: str,
        art_style: str,
        custom_setting: str | None = None,
    ) -> ComicModel:
        """Create a new comic record."""
        comic = ComicModel(
            id=comic_id,
            prompt=prompt,
            character_name=character_name,
            setting=setting,
            custom_setting=custom_setting,
            tone=tone,
            art_style=art_style,
            status="queued",
        )
        self.session.add(comic)
        await self.session.commit()
        await self.session.refresh(comic)
        return comic

    async def update(
        self,
        comic_id: str,
        *,
        status: str | None = None,
        title: str | None = None,
        synopsis: str | None = None,
        character_sheet: dict[str, Any] | None = None,
        panels: list[dict[str, Any]] | None = None,
        pdf_path: str | None = None,
        tone: str | None = None,
        art_style: str | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> ComicModel | None:
        """Update fields on existing comic."""
        comic = await self.get_by_id(comic_id)
        if not comic:
            return None

        if status is not None:
            comic.status = status
        if title is not None:
            comic.title = title
        if synopsis is not None:
            comic.synopsis = synopsis
        if character_sheet is not None:
            comic.character_sheet = character_sheet
        if panels is not None:
            comic.panels = panels
        if pdf_path is not None:
            comic.pdf_path = pdf_path
        if tone is not None:
            comic.tone = tone
        if art_style is not None:
            comic.art_style = art_style
        if error_code is not None:
            comic.error_code = error_code
        if error_message is not None:
            comic.error_message = error_message

        await self.session.commit()
        await self.session.refresh(comic)
        return comic


class JobRepository:
    """Repository handling CRUD operations for jobs."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, job_id: str) -> JobModel | None:
        """Fetch job by ID."""
        stmt = select(JobModel).where(JobModel.id == job_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_latest_by_comic_id(self, comic_id: str) -> JobModel | None:
        """Fetch latest job for comic."""
        stmt = (
            select(JobModel)
            .where(JobModel.comic_id == comic_id)
            .order_by(JobModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create(self, job_id: str, comic_id: str) -> JobModel:
        """Create a new job record."""
        job = JobModel(
            id=job_id,
            comic_id=comic_id,
            stage="queued",
            progress=0,
            status="in_progress",
        )
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def update_progress(
        self,
        job_id: str,
        stage: str,
        progress: int,
        status: str = "in_progress",
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> JobModel | None:
        """Update job stage and progress percentage."""
        job = await self.get_by_id(job_id)
        if not job:
            return None

        job.stage = stage
        job.progress = progress
        job.status = status
        if error_code:
            job.error_code = error_code
        if error_message:
            job.error_message = error_message

        await self.session.commit()
        await self.session.refresh(job)
        return job

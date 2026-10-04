"""Asynchronous pipeline orchestrator for comic generation."""

from app.ai import BaseAIService, CharacterSheet, ComicScriptSchema, GeminiAIService
from app.ai.image_providers import ImageProvider, get_image_provider
from app.core.config import settings
from app.core.logging import get_logger
from app.db.database import async_session_factory
from app.db.repositories import ComicRepository, JobRepository
from app.schemas.events import ComicEvent
from app.services.character_service import CharacterService
from app.services.job_service import broadcaster

logger = get_logger(__name__)


class GenerationService:
    """Orchestrates asynchronous, end-to-end comic generation."""

    def __init__(
        self,
        ai_service: BaseAIService | None = None,
        image_provider: ImageProvider | None = None,
    ) -> None:
        self.ai_service = ai_service or GeminiAIService()
        self.character_service = CharacterService(provider=image_provider or get_image_provider())

    async def run_pipeline(self, comic_id: str, job_id: str) -> None:
        """Execute full async generation pipeline in background."""
        logger.info(f"Starting comic generation pipeline for comic [{comic_id}] / job [{job_id}]")

        async with async_session_factory() as session:
            comic_repo = ComicRepository(session)
            job_repo = JobRepository(session)

            comic = await comic_repo.get_by_id(comic_id)
            if not comic:
                logger.error(f"Comic [{comic_id}] not found in database.")
                return

            try:
                # Stage 1: Queued
                await job_repo.update_progress(job_id, stage="queued", progress=5)
                await broadcaster.broadcast(
                    comic_id,
                    ComicEvent(
                        stage="queued",
                        progress=5,
                        message="Generation request initialized in queue.",
                        comic_id=comic_id,
                        job_id=job_id,
                    ),
                )

                # Stage 2: Character Sheet / Outline
                await job_repo.update_progress(job_id, stage="outline", progress=20)
                await broadcaster.broadcast(
                    comic_id,
                    ComicEvent(
                        stage="outline",
                        progress=20,
                        message="Crafting canonical character visual identity...",
                        comic_id=comic_id,
                        job_id=job_id,
                    ),
                )

                char_sheet: CharacterSheet = await self.ai_service.generate_character_sheet(
                    character_name=comic.character_name,
                    story_prompt=comic.prompt,
                    setting=comic.setting,
                    art_style=comic.art_style,
                )
                await comic_repo.update(comic_id, character_sheet=char_sheet.model_dump())

                # Stage 3: Story Outline & Narration (5 Panels)
                await job_repo.update_progress(job_id, stage="story", progress=40)
                await broadcaster.broadcast(
                    comic_id,
                    ComicEvent(
                        stage="story",
                        progress=40,
                        message="Directing 5-panel story arc, narration, and dialogue...",
                        comic_id=comic_id,
                        job_id=job_id,
                    ),
                )

                script: ComicScriptSchema = await self.ai_service.generate_comic_script(
                    story_prompt=comic.prompt,
                    character_sheet=char_sheet,
                    setting=comic.setting,
                    tone=comic.tone,
                    art_style=comic.art_style,
                    custom_setting=comic.custom_setting,
                )
                await comic_repo.update(
                    comic_id,
                    title=script.title,
                    synopsis=script.synopsis,
                )

                # Stage 4: Image Generation Preparation
                await job_repo.update_progress(job_id, stage="images", progress=50)
                await broadcaster.broadcast(
                    comic_id,
                    ComicEvent(
                        stage="images",
                        progress=50,
                        message="Starting bounded concurrent panel illustration...",
                        comic_id=comic_id,
                        job_id=job_id,
                    ),
                )

                # Ensure image storage folder for comic exists
                comic_img_dir = settings.images_storage_path / comic_id
                comic_img_dir.mkdir(parents=True, exist_ok=True)

                # Progress callback for individual panel completion
                async def _on_panel_ready(panel_idx: int, img_bytes: bytes) -> None:
                    # Save image file to storage
                    file_path = comic_img_dir / f"panel_{panel_idx}.png"
                    file_path.write_bytes(img_bytes)

                    rel_url = f"/storage/images/{comic_id}/panel_{panel_idx}.png"
                    panel_progress = 50 + int((panel_idx / 5.0) * 30)  # 56% to 80%

                    stage_name = f"image_panel_{panel_idx}"
                    # Find matching panel data from script
                    matched_panel = next((p for p in script.panels if p.panel == panel_idx), None)
                    p_data = matched_panel.model_dump() if matched_panel else {}
                    p_data["image_url"] = rel_url

                    await broadcaster.broadcast(
                        comic_id,
                        ComicEvent(
                            stage=stage_name,
                            progress=panel_progress,
                            message=f"Panel {panel_idx} of 5 illustrated.",
                            comic_id=comic_id,
                            job_id=job_id,
                            panel_index=panel_idx,
                            panel_data=p_data,
                        ),
                    )

                # Generate all panel images concurrently
                _ = await self.character_service.generate_all_panel_images(
                    panels=script.panels,
                    character_sheet=char_sheet,
                    art_style=comic.art_style,
                    on_panel_progress=_on_panel_ready,
                )

                # Stage 5: Comic Assembly & Layout
                await job_repo.update_progress(job_id, stage="layout", progress=90)
                await broadcaster.broadcast(
                    comic_id,
                    ComicEvent(
                        stage="layout",
                        progress=90,
                        message="Assembling panels, speech bubbles, and visual layout...",
                        comic_id=comic_id,
                        job_id=job_id,
                    ),
                )

                # Build final panels JSON array
                final_panels = []
                for p in script.panels:
                    p_dict = p.model_dump()
                    p_dict["image_url"] = f"/storage/images/{comic_id}/panel_{p.panel}.png"
                    final_panels.append(p_dict)

                await comic_repo.update(
                    comic_id,
                    panels=final_panels,
                    status="completed",
                )

                # Stage 6: Ready
                await job_repo.update_progress(
                    job_id, stage="ready", progress=100, status="completed"
                )
                await broadcaster.broadcast(
                    comic_id,
                    ComicEvent(
                        stage="ready",
                        progress=100,
                        message="Your 5-panel comic is ready!",
                        comic_id=comic_id,
                        job_id=job_id,
                    ),
                )
                logger.info(f"Comic generation successfully completed for comic [{comic_id}]")

            except Exception as exc:
                logger.exception(f"Comic generation pipeline failed for comic [{comic_id}]: {exc}")
                error_msg = str(exc)
                await comic_repo.update(
                    comic_id,
                    status="failed",
                    error_code="GENERATION_FAILED",
                    error_message=error_msg,
                )
                await job_repo.update_progress(
                    job_id,
                    stage="failed",
                    progress=100,
                    status="failed",
                    error_code="GENERATION_FAILED",
                    error_message=error_msg,
                )
                await broadcaster.broadcast(
                    comic_id,
                    ComicEvent(
                        stage="failed",
                        progress=100,
                        message=f"Comic generation failed: {error_msg}",
                        comic_id=comic_id,
                        job_id=job_id,
                        error=error_msg,
                    ),
                )


# Global generation service singleton
generation_service = GenerationService()

"""Service orchestrating character consistency, style injection, and concurrent panel illustration."""

import asyncio
from collections.abc import Callable, Coroutine

from app.ai.image_providers import ImageProvider, get_image_provider
from app.ai.prompts import get_art_style
from app.ai.schemas import CharacterSheet, PanelSchema
from app.core.config import settings
from app.core.errors import GenerationException
from app.core.logging import get_logger

logger = get_logger(__name__)


class CharacterService:
    """Coordinates character consistency and bounded concurrent panel generation."""

    def __init__(self, provider: ImageProvider | None = None) -> None:
        self.provider = provider or get_image_provider()
        self.concurrency_limit = settings.IMAGE_CONCURRENCY_LIMIT

    def compose_panel_prompt(
        self,
        panel: PanelSchema,
        character_sheet: CharacterSheet,
        art_style: str,
    ) -> tuple[str, str]:
        """Compose image prompt prepending character identity, scene directions, and style anchors."""
        style_preset = get_art_style(art_style)
        char_desc = (
            f"{character_sheet.name}, wearing {character_sheet.outfit}, "
            f"hair: {character_sheet.hair}, eyes: {character_sheet.eyes}, "
            f"distinctive marks: {', '.join(character_sheet.distinctive_features) if character_sheet.distinctive_features else 'none'}"
        )

        final_positive_prompt = (
            f"Comic panel illustration of {char_desc}. "
            f"Scene: {panel.scene_description}. "
            f"Visual action: {panel.image_prompt}. "
            f"Style: {style_preset.positive_prompt_fragment}."
        )

        final_negative_prompt = style_preset.negative_prompt
        return final_positive_prompt, final_negative_prompt

    async def generate_all_panel_images(
        self,
        panels: list[PanelSchema],
        character_sheet: CharacterSheet,
        art_style: str,
        on_panel_progress: Callable[[int, bytes], Coroutine[None, None, None]] | None = None,
    ) -> dict[int, bytes]:
        """
        Generate images for all 5 panels with bounded concurrency and character reference propagation.
        Sequential panel 1 first for reference anchor, then panels 2-5 concurrently.
        """
        results: dict[int, bytes] = {}
        semaphore = asyncio.Semaphore(self.concurrency_limit)

        # 1. Generate Panel 1 first as reference anchor
        p1 = panels[0]
        p1_prompt, p1_neg = self.compose_panel_prompt(p1, character_sheet, art_style)
        logger.info(f"Generating Panel 1 reference image (Character: {character_sheet.name})")

        p1_bytes = await self.provider.generate_panel_image(
            prompt=p1_prompt,
            negative_prompt=p1_neg,
            reference_image=None,
        )
        results[1] = p1_bytes
        if on_panel_progress:
            await on_panel_progress(1, p1_bytes)

        # 2. Worker for remaining panels (2-5) bounded by semaphore
        async def _generate_single_panel(panel: PanelSchema) -> None:
            async with semaphore:
                logger.info(f"Generating Panel {panel.panel} artwork (concurrency bound)")
                prompt, neg_prompt = self.compose_panel_prompt(panel, character_sheet, art_style)
                img_bytes = await self.provider.generate_panel_image(
                    prompt=prompt,
                    negative_prompt=neg_prompt,
                    reference_image=p1_bytes,
                )
                results[panel.panel] = img_bytes
                if on_panel_progress:
                    await on_panel_progress(panel.panel, img_bytes)

        tasks = [_generate_single_panel(p) for p in panels[1:]]
        # Return exceptions rather than abruptly aborting other panels
        execution_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify any panel failures
        failed_panels: list[int] = []
        for p, res in zip(panels[1:], execution_results, strict=False):
            if isinstance(res, Exception):
                logger.error(f"Panel {p.panel} image generation failed: {res}")
                failed_panels.append(p.panel)

        if failed_panels:
            raise GenerationException(
                f"Failed to generate artwork for panels: {failed_panels}",
                code="PANEL_IMAGE_FAILED",
            )

        return results

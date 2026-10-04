"""Tests for ImageProvider implementations and CharacterService."""

import io
from unittest.mock import AsyncMock, MagicMock

import pytest
from PIL import Image

from app.ai.image_providers import (
    DiffusersImageProvider,
    GeminiImageProvider,
    get_image_provider,
)
from app.ai.schemas import CharacterSheet, DialogueItem, PanelSchema
from app.core.errors import GenerationException
from app.services.character_service import CharacterService


def create_dummy_png_bytes(color: tuple[int, int, int] = (255, 0, 0)) -> bytes:
    """Helper creating raw valid PNG bytes."""
    img = Image.new("RGB", (100, 100), color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def sample_character() -> CharacterSheet:
    return CharacterSheet(
        name="Free",
        appearance="A brave fox with bright amber eyes",
        age_presentation="Young adult",
        hair="Russet fur",
        face="Sharp muzzle",
        eyes="Amber",
        outfit="Green traveler's cloak",
        primary_colors=["Orange", "Green"],
        accessories=["Leaf pin"],
        distinctive_features=["Ear notch"],
    )


@pytest.fixture
def sample_panels() -> list[PanelSchema]:
    return [
        PanelSchema(
            panel=i,
            title=f"Panel {i}",
            scene_description=f"Scene {i} description in forest",
            caption=f"Caption {i}",
            narration=f"Narration {i}",
            dialogue=[DialogueItem(speaker="Free", text=f"Dialogue {i}")],
            image_prompt=f"Prompt for panel {i} with dramatic camera angle",
        )
        for i in range(1, 6)
    ]


@pytest.mark.asyncio
async def test_gemini_image_provider_mocked() -> None:
    """Ensure GeminiImageProvider returns valid PNG bytes from mocked response."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    dummy_bytes = create_dummy_png_bytes()

    mock_generated_image = MagicMock()
    mock_generated_image.rai_filtered_reason = None
    mock_generated_image.image.image_bytes = dummy_bytes
    mock_response.generated_images = [mock_generated_image]

    mock_client.aio.models.generate_images = AsyncMock(return_value=mock_response)

    provider = GeminiImageProvider(api_key="mock_key", client=mock_client)
    result = await provider.generate_panel_image(
        prompt="Test prompt",
        negative_prompt="Test neg",
    )

    assert isinstance(result, bytes)
    assert len(result) > 0
    # Verify valid image format
    with Image.open(io.BytesIO(result)) as pil_img:
        assert pil_img.format == "PNG"


@pytest.mark.asyncio
async def test_gemini_image_provider_safety_filter() -> None:
    """Ensure GeminiImageProvider raises GenerationException on safety filter violation."""
    mock_client = MagicMock()
    mock_response = MagicMock()

    mock_generated_image = MagicMock()
    mock_generated_image.rai_filtered_reason = "SAFETY_VIOLATION_HARASSMENT"
    mock_response.generated_images = [mock_generated_image]

    mock_client.aio.models.generate_images = AsyncMock(return_value=mock_response)

    provider = GeminiImageProvider(api_key="mock_key", client=mock_client)
    with pytest.raises(GenerationException) as exc_info:
        await provider.generate_panel_image(
            prompt="Unsafe prompt",
            negative_prompt="neg",
        )
    assert exc_info.value.code == "CONTENT_FILTERED"


@pytest.mark.asyncio
async def test_diffusers_image_provider_fallback() -> None:
    """Ensure DiffusersImageProvider creates high quality canvas fallback without crash."""
    provider = DiffusersImageProvider()
    result = await provider.generate_panel_image(
        prompt="Free the fox exploring enchanted trees",
        negative_prompt="blurry",
    )
    assert isinstance(result, bytes)
    with Image.open(io.BytesIO(result)) as pil_img:
        assert pil_img.format == "PNG"
        assert pil_img.size == (800, 600)


def test_get_image_provider_factory() -> None:
    """Verify factory returns appropriate provider instance."""
    gemini_prov = get_image_provider("gemini")
    assert isinstance(gemini_prov, GeminiImageProvider)

    diffusers_prov = get_image_provider("diffusers")
    assert isinstance(diffusers_prov, DiffusersImageProvider)


@pytest.mark.asyncio
async def test_character_service_generate_all_panels(
    sample_panels: list[PanelSchema],
    sample_character: CharacterSheet,
) -> None:
    """Verify CharacterService bounded generation executes for all 5 panels."""
    mock_provider = MagicMock()
    dummy_bytes = create_dummy_png_bytes()
    mock_provider.generate_panel_image = AsyncMock(return_value=dummy_bytes)

    service = CharacterService(provider=mock_provider)
    progress_calls: list[int] = []

    async def on_progress(p_idx: int, _data: bytes) -> None:
        progress_calls.append(p_idx)

    images = await service.generate_all_panel_images(
        panels=sample_panels,
        character_sheet=sample_character,
        art_style="Anime",
        on_panel_progress=on_progress,
    )

    assert len(images) == 5
    for i in range(1, 6):
        assert i in images
    assert sorted(progress_calls) == [1, 2, 3, 4, 5]
    assert mock_provider.generate_panel_image.call_count == 5


@pytest.mark.asyncio
async def test_character_service_handles_panel_failure(
    sample_panels: list[PanelSchema],
    sample_character: CharacterSheet,
) -> None:
    """Verify failure in one panel raises GenerationException without marking success."""
    mock_provider = MagicMock()
    dummy_bytes = create_dummy_png_bytes()

    # Fail on panel 3
    async def side_effect(prompt: str, **kwargs: object) -> bytes:
        if "panel 3" in prompt.lower():
            raise RuntimeError("GPU OOM on panel 3")
        return dummy_bytes

    mock_provider.generate_panel_image = AsyncMock(side_effect=side_effect)

    service = CharacterService(provider=mock_provider)
    with pytest.raises(GenerationException) as exc_info:
        await service.generate_all_panel_images(
            panels=sample_panels,
            character_sheet=sample_character,
            art_style="Anime",
        )

    assert exc_info.value.code == "PANEL_IMAGE_FAILED"
    assert "3" in str(exc_info.value)

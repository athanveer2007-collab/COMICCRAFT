"""Unit and integration tests for the AI generation layer with offline mocks."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from google.genai.errors import APIError
from pydantic import ValidationError

from app.ai.gemini import GeminiAIService
from app.ai.prompts import (
    get_art_style,
    get_tone,
)
from app.ai.schemas import (
    CharacterSheet,
    ComicScriptSchema,
    DialogueItem,
    PanelSchema,
)
from app.core.errors import GenerationException

# --- Fixtures ---


@pytest.fixture
def sample_character_sheet() -> CharacterSheet:
    return CharacterSheet(
        name="Free",
        appearance="A clever red fox with agile stance and bright amber eyes",
        age_presentation="Young adult",
        hair="Thick russet fur with white tipped tail",
        face="Sleek muzzle with whiskers and alert pointed ears",
        eyes="Glowing amber-gold eyes full of curiosity",
        outfit="Weathered traveler's cloak with silver leaf clasp",
        primary_colors=["Russet orange", "Forest green", "Silver"],
        accessories=["Woven leather satchel", "Ancient map scroll"],
        distinctive_features=["Small notch on left ear tip"],
    )


@pytest.fixture
def sample_five_panels() -> list[PanelSchema]:
    return [
        PanelSchema(
            panel=1,
            title="The Edge of the Woods",
            scene_description="Free stands at the shadowy border of the glowing forest, looking at the twisted trees.",
            caption="The Whisperwood had slept for a thousand years.",
            narration="Free tightened his cloak against the eerie, luminescent breeze.",
            dialogue=[DialogueItem(speaker="Free", text="There's no turning back now.")],
            image_prompt="Wide shot of Free the fox in a green cloak standing before towering enchanted trees, anime style.",
        ),
        PanelSchema(
            panel=2,
            title="The Luminous Trail",
            scene_description="Free discovers ethereal glowing blue tracks winding deep between ancient roots.",
            caption="Ancient tracks whispered of forgotten magic.",
            narration="Every footprint pulsed with soft starlight.",
            dialogue=[DialogueItem(speaker="Free", text="The legend was real...")],
            image_prompt="Medium low-angle shot of Free kneeling beside glowing blue footsteps on mossy ground, anime style.",
        ),
        PanelSchema(
            panel=3,
            title="The Guardian's Shadow",
            scene_description="A massive crystalline stag emerges from the canopy, eyes glowing with sacred fire.",
            caption="A guardian awaken from emerald slumber.",
            narration="The air crackled with raw, ancient authority.",
            dialogue=[DialogueItem(speaker="Guardian", text="Who dares disturb the roots?")],
            image_prompt="Dramatic eye-level shot of a crystalline stag towering over Free the fox, anime style.",
        ),
        PanelSchema(
            panel=4,
            title="A Humble Offering",
            scene_description="Free draws the silver leaf clasp from his cloak, holding it high in peaceful homage.",
            caption="Courage does not always wield a sword.",
            narration="Free stepped forward, meeting the guardian's luminous gaze without flinching.",
            dialogue=[DialogueItem(speaker="Free", text="I seek only knowledge of the stars.")],
            image_prompt="Close-up of Free holding up a silver leaf clasp emitting gentle light, anime style.",
        ),
        PanelSchema(
            panel=5,
            title="Path of the Starweaver",
            scene_description="The stag bows its head, and the dense forest canopy parts to reveal a constellation trail.",
            caption="The forest grants passage to the worthy.",
            narration="With the guardian's blessing, the uncharted journey truly began.",
            dialogue=[DialogueItem(speaker="Free", text="To the stars, then.")],
            image_prompt="Wide cinematic silhouette of Free walking toward a starry opening in the canopy, anime style.",
        ),
    ]


@pytest.fixture
def sample_comic_script(
    sample_character_sheet: CharacterSheet, sample_five_panels: list[PanelSchema]
) -> ComicScriptSchema:
    return ComicScriptSchema(
        title="Chronicles of the Whisperwood",
        synopsis="A brave fox named Free ventures into the legendary Enchanted Forest and earns the favor of an ancient guardian.",
        character_sheet=sample_character_sheet,
        panels=sample_five_panels,
    )


# --- Schema Tests ---


def test_comic_script_requires_exactly_five_panels(
    sample_character_sheet: CharacterSheet, sample_five_panels: list[PanelSchema]
) -> None:
    """Validate that less than 5 panels raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        ComicScriptSchema(
            title="Incomplete Comic",
            synopsis="This comic only has four panels.",
            character_sheet=sample_character_sheet,
            panels=sample_five_panels[:4],
        )
    assert "panels" in str(exc_info.value)


def test_comic_script_rejects_out_of_order_panels(
    sample_character_sheet: CharacterSheet, sample_five_panels: list[PanelSchema]
) -> None:
    """Validate that disordered panel numbering raises ValidationError."""
    broken_panels = list(sample_five_panels)
    broken_panels[0] = broken_panels[0].model_copy(update={"panel": 2})

    with pytest.raises(ValidationError) as exc_info:
        ComicScriptSchema(
            title="Disordered Comic",
            synopsis="Panels are out of sequential order.",
            character_sheet=sample_character_sheet,
            panels=broken_panels,
        )
    assert "expected 1" in str(exc_info.value)


def test_character_sheet_to_prompt_summary(sample_character_sheet: CharacterSheet) -> None:
    """Ensure character sheet summary formats correctly for prompt injection."""
    summary = sample_character_sheet.to_prompt_summary()
    assert "Free" in summary
    assert "Russet orange" in summary
    assert "cloak" in summary


# --- Prompt & Preset Tests ---


def test_style_presets_contain_required_styles() -> None:
    """Ensure Anime, Pixel Art, Comic Book, and Realistic styles are defined with negative prompts."""
    required = ["Anime", "Pixel Art", "Comic Book", "Realistic"]
    for style_name in required:
        style = get_art_style(style_name)
        assert style.name == style_name
        assert style.positive_prompt_fragment
        assert "watermark" in style.negative_prompt
        assert "bad anatomy" in style.negative_prompt


def test_tone_presets_contain_required_tones() -> None:
    """Ensure Light-hearted, Dramatic, Poetic, and Funny tones are defined."""
    required = ["Light-hearted", "Dramatic", "Poetic", "Funny"]
    for tone_name in required:
        tone = get_tone(tone_name)
        assert tone.name == tone_name
        assert tone.narrative_characteristics
        assert tone.dialogue_characteristics
        assert tone.visual_mood


# --- Gemini Service Offline Mock Tests ---


@pytest.mark.asyncio
async def test_generate_character_sheet_mocked(sample_character_sheet: CharacterSheet) -> None:
    """Verify GeminiAIService parses structured character sheet from mocked client."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.parsed = sample_character_sheet

    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    service = GeminiAIService(api_key="mock_key", client=mock_client)
    result = await service.generate_character_sheet(
        character_name="Free",
        story_prompt="A brave fox exploring an enchanted forest",
        setting="Forest",
        art_style="Anime",
    )

    assert result.name == "Free"
    assert "amber" in result.eyes.lower()
    mock_client.aio.models.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_generate_comic_script_mocked(
    sample_character_sheet: CharacterSheet,
    sample_comic_script: ComicScriptSchema,
) -> None:
    """Verify GeminiAIService parses 5-panel comic script from mocked client."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.parsed = sample_comic_script

    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    service = GeminiAIService(api_key="mock_key", client=mock_client)
    result = await service.generate_comic_script(
        story_prompt="A brave fox exploring an enchanted forest",
        character_sheet=sample_character_sheet,
        setting="Forest",
        tone="Dramatic",
        art_style="Anime",
    )

    assert len(result.panels) == 5
    assert result.panels[0].panel == 1
    assert result.panels[4].panel == 5
    assert result.title == "Chronicles of the Whisperwood"


@pytest.mark.asyncio
async def test_gemini_service_retries_transient_api_error(
    sample_character_sheet: CharacterSheet,
) -> None:
    """Verify tenacity retries on transient APIError before succeeding."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.parsed = sample_character_sheet

    # Simulate 1 transient API error followed by success
    transient_error = APIError(429, {"message": "Temporary rate limit 429"})
    mock_client.aio.models.generate_content = AsyncMock(
        side_effect=[transient_error, mock_response]
    )

    service = GeminiAIService(api_key="mock_key", client=mock_client)
    result = await service.generate_character_sheet(
        character_name="Free",
        story_prompt="Story prompt",
        setting="Forest",
        art_style="Anime",
    )

    assert result.name == "Free"
    assert mock_client.aio.models.generate_content.call_count == 2


@pytest.mark.asyncio
async def test_gemini_service_raises_generation_exception_on_empty_response() -> None:
    """Verify empty response raises GenerationException."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.parsed = None
    mock_response.text = None

    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    service = GeminiAIService(api_key="mock_key", client=mock_client)
    with pytest.raises(GenerationException) as exc_info:
        await service.generate_character_sheet(
            character_name="Free",
            story_prompt="Story prompt",
            setting="Forest",
            art_style="Anime",
        )
    assert exc_info.value.code == "EMPTY_AI_RESPONSE"

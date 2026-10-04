"""Schemas for Comic creation, regeneration, and response representation."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.ai.prompts import ART_STYLE_PRESETS, TONE_PRESETS
from app.ai.schemas import CharacterSheet, DialogueItem


class ComicCreateRequest(BaseModel):
    """Payload to initiate a new comic generation."""

    prompt: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="The story concept or plot idea",
        examples=["A brave fox exploring an enchanted forest"],
    )
    character_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Main protagonist name",
        examples=["Free"],
    )
    setting: str = Field(
        default="Forest",
        description="Setting of the comic (School, Forest, Space, City, or Custom setting)",
        examples=["Forest"],
    )
    custom_setting: str | None = Field(
        default=None,
        max_length=200,
        description="Custom setting name if setting is 'Custom setting'",
    )
    tone: str = Field(
        default="Dramatic",
        description="Narrative tone (Light-hearted, Dramatic, Poetic, Funny)",
        examples=["Dramatic"],
    )
    art_style: str = Field(
        default="Anime",
        description="Visual style (Anime, Pixel Art, Comic Book, Realistic)",
        examples=["Anime"],
    )

    @field_validator("tone")
    @classmethod
    def validate_tone(cls, v: str) -> str:
        matched = next((k for k in TONE_PRESETS if k.lower() == v.lower()), None)
        if not matched:
            raise ValueError(
                f"Unsupported tone '{v}'. Supported tones: {list(TONE_PRESETS.keys())}"
            )
        return matched

    @field_validator("art_style")
    @classmethod
    def validate_art_style(cls, v: str) -> str:
        matched = next((k for k in ART_STYLE_PRESETS if k.lower() == v.lower()), None)
        if not matched:
            raise ValueError(
                f"Unsupported art style '{v}'. Supported styles: {list(ART_STYLE_PRESETS.keys())}"
            )
        return matched

    @field_validator("custom_setting")
    @classmethod
    def validate_custom_setting(cls, v: str | None, info: object) -> str | None:
        # Validate that custom_setting is provided if setting is Custom setting
        return v


class ComicRegenerateRequest(BaseModel):
    """Payload to regenerate an existing comic with different tone and/or art style."""

    tone: str | None = Field(
        default=None,
        description="Updated narrative tone (Light-hearted, Dramatic, Poetic, Funny)",
    )
    art_style: str | None = Field(
        default=None,
        description="Updated visual style (Anime, Pixel Art, Comic Book, Realistic)",
    )

    @field_validator("tone")
    @classmethod
    def validate_tone(cls, v: str | None) -> str | None:
        if v is None:
            return None
        matched = next((k for k in TONE_PRESETS if k.lower() == v.lower()), None)
        if not matched:
            raise ValueError(
                f"Unsupported tone '{v}'. Supported tones: {list(TONE_PRESETS.keys())}"
            )
        return matched

    @field_validator("art_style")
    @classmethod
    def validate_art_style(cls, v: str | None) -> str | None:
        if v is None:
            return None
        matched = next((k for k in ART_STYLE_PRESETS if k.lower() == v.lower()), None)
        if not matched:
            raise ValueError(
                f"Unsupported art style '{v}'. Supported styles: {list(ART_STYLE_PRESETS.keys())}"
            )
        return matched


class PanelResponse(BaseModel):
    """Structured response for a single comic panel."""

    panel: int
    title: str
    scene_description: str
    caption: str
    narration: str
    dialogue: list[DialogueItem] = Field(default_factory=list)
    image_prompt: str
    image_url: str | None = None


class ComicResponse(BaseModel):
    """Full comic presentation response."""

    id: str
    prompt: str
    character_name: str
    setting: str
    custom_setting: str | None = None
    tone: str
    art_style: str
    title: str | None = None
    synopsis: str | None = None
    character_sheet: CharacterSheet | None = None
    status: str
    panels: list[PanelResponse] | None = None
    pdf_path: str | None = None
    pdf_url: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

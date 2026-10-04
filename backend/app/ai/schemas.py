"""Pydantic schemas for AI-driven comic generation and structured outputs."""

from pydantic import BaseModel, Field, field_validator


class CharacterSheet(BaseModel):
    """Canonical visual and thematic identity for the main character."""

    name: str = Field(..., min_length=1, max_length=100, description="Character's name")
    appearance: str = Field(..., max_length=500, description="Overall physical summary")
    age_presentation: str = Field(..., max_length=50, description="Estimated visual age range")
    hair: str = Field(..., max_length=200, description="Hairstyle, color, and texture")
    face: str = Field(..., max_length=200, description="Facial shape and structure")
    eyes: str = Field(..., max_length=200, description="Eye color, shape, and expression")
    outfit: str = Field(..., max_length=500, description="Signature clothing and materials")
    primary_colors: list[str] = Field(..., min_length=1, description="Primary iconic color palette")
    accessories: list[str] = Field(
        default_factory=list, description="Signature accessories or gear"
    )
    distinctive_features: list[str] = Field(
        default_factory=list, description="Unique identifying marks (scars, logos, glowing traits)"
    )

    def to_prompt_summary(self) -> str:
        """Serialize character sheet into a condensed prompt injection block."""
        colors = ", ".join(self.primary_colors)
        acc = ", ".join(self.accessories) if self.accessories else "None"
        features = ", ".join(self.distinctive_features) if self.distinctive_features else "None"
        return (
            f"Character: {self.name} | Appearance: {self.appearance} | "
            f"Hair: {self.hair} | Face: {self.face} | Eyes: {self.eyes} | "
            f"Outfit: {self.outfit} | Colors: {colors} | Accessories: {acc} | "
            f"Distinctive: {features}"
        )


class DialogueItem(BaseModel):
    """Speech or thought dialogue within a panel."""

    speaker: str = Field(..., min_length=1, max_length=60, description="Speaker name")
    text: str = Field(..., min_length=1, max_length=250, description="Spoken dialogue text")


class PanelSchema(BaseModel):
    """Structured representation of an individual comic panel."""

    panel: int = Field(..., ge=1, le=5, description="1-indexed panel sequence number")
    title: str = Field(..., min_length=1, max_length=100, description="Panel title or beat name")
    scene_description: str = Field(
        ..., min_length=10, max_length=600, description="Detailed scene visual composition"
    )
    caption: str = Field(
        ..., max_length=250, description="Atmospheric caption or location/time subtitle"
    )
    narration: str = Field(
        ..., max_length=400, description="Narrator box text framing the dramatic action"
    )
    dialogue: list[DialogueItem] = Field(
        default_factory=list, max_length=4, description="Dialogue lines between characters"
    )
    image_prompt: str = Field(
        ...,
        min_length=20,
        max_length=1200,
        description="Detailed, self-contained prompt for image generator incorporating character consistency and style anchors",
    )


class ComicScriptSchema(BaseModel):
    """Full 5-panel comic story script."""

    title: str = Field(..., min_length=1, max_length=150, description="Comic overall title")
    synopsis: str = Field(
        ..., min_length=20, max_length=800, description="High-level narrative arc"
    )
    character_sheet: CharacterSheet = Field(..., description="Canonical character visual identity")
    panels: list[PanelSchema] = Field(
        ..., min_length=5, max_length=5, description="Exact 5-panel story sequence"
    )

    @field_validator("panels")
    @classmethod
    def validate_panel_count_and_order(cls, panels: list[PanelSchema]) -> list[PanelSchema]:
        """Enforce exactly 5 sequential panels from 1 to 5."""
        if len(panels) != 5:
            raise ValueError(f"Comic must contain exactly 5 panels, got {len(panels)}")
        for idx, panel in enumerate(panels, start=1):
            if panel.panel != idx:
                raise ValueError(
                    f"Panel at index {idx - 1} has panel number {panel.panel}; expected {idx}"
                )
        return panels


class StoryOutline(BaseModel):
    """Intermediate high-level outline before full panel drafting."""

    title: str = Field(..., max_length=150)
    premise: str = Field(..., max_length=500)
    character_sheet: CharacterSheet
    panel_beats: list[str] = Field(
        ..., min_length=5, max_length=5, description="5 sequential narrative beats"
    )

    @field_validator("panel_beats")
    @classmethod
    def validate_five_beats(cls, beats: list[str]) -> list[str]:
        if len(beats) != 5:
            raise ValueError(f"Outline must have exactly 5 panel beats, got {len(beats)}")
        return beats

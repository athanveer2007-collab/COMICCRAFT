"""Abstract interface for AI text and narrative generation services."""

from abc import ABC, abstractmethod

from app.ai.schemas import CharacterSheet, ComicScriptSchema


class BaseAIService(ABC):
    """Abstract interface defining required AI narrative and script generation methods."""

    @abstractmethod
    async def generate_character_sheet(
        self,
        character_name: str,
        story_prompt: str,
        setting: str,
        art_style: str,
    ) -> CharacterSheet:
        """Generate canonical visual character attributes."""
        pass

    @abstractmethod
    async def generate_comic_script(
        self,
        story_prompt: str,
        character_sheet: CharacterSheet,
        setting: str,
        tone: str,
        art_style: str,
        custom_setting: str | None = None,
    ) -> ComicScriptSchema:
        """Generate complete 5-panel comic story outline, dialogue, and image prompts."""
        pass

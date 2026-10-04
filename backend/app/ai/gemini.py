"""Gemini AI implementation using official google-genai SDK with structured output."""

from typing import Any

from google import genai
from google.genai import types
from google.genai.errors import APIError
from pydantic import ValidationError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from app.ai.base import BaseAIService
from app.ai.prompts import (
    build_character_sheet_prompt,
    build_comic_script_prompt,
)
from app.ai.schemas import CharacterSheet, ComicScriptSchema
from app.core.config import settings
from app.core.errors import GenerationException
from app.core.logging import get_logger

logger = get_logger(__name__)


class GeminiAIService(BaseAIService):
    """Production Gemini AI service implementing BaseAIService with structured schemas."""

    def __init__(self, api_key: str | None = None, client: genai.Client | None = None) -> None:
        self.api_key = api_key or settings.GOOGLE_API_KEY
        if client:
            self.client = client
        else:
            self.client = genai.Client(api_key=self.api_key)

    @retry(
        retry=retry_if_exception_type((APIError, ConnectionError, TimeoutError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(initial=1, max=8),
        reraise=True,
    )
    async def _call_gemini_structured(
        self,
        model: str,
        prompt: str,
        response_schema: Any,
    ) -> Any:
        """Call Gemini model asynchronously with strict structured output enforcement."""
        logger.info(
            f"Invoking Gemini model [{model}] for structured schema [{response_schema.__name__}]"
        )

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema,
            temperature=0.7,
        )

        try:
            response = await self.client.aio.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )

            # Check for structured parsed response or fallback to JSON text validation
            if hasattr(response, "parsed") and response.parsed is not None:
                return response.parsed

            if hasattr(response, "text") and response.text:
                return response_schema.model_validate_json(response.text)

            raise GenerationException(
                "Gemini model returned empty response content.",
                code="EMPTY_AI_RESPONSE",
            )
        except ValidationError as val_err:
            logger.error(f"Pydantic schema validation failed on Gemini output: {val_err}")
            raise GenerationException(
                f"Generated content violated schema: {val_err}",
                code="INVALID_STRUCTURED_OUTPUT",
            ) from val_err
        except GenerationException:
            raise
        except APIError as api_err:
            logger.error(f"Gemini API error occurred: {api_err}")
            raise
        except Exception as exc:
            logger.error(f"Unexpected error in Gemini generation: {exc}")
            raise GenerationException(
                f"AI generation failed: {exc}",
                code="GENERATION_FAILED",
            ) from exc

    async def generate_character_sheet(
        self,
        character_name: str,
        story_prompt: str,
        setting: str,
        art_style: str,
    ) -> CharacterSheet:
        """Generate canonical visual attributes for the main character."""
        prompt = build_character_sheet_prompt(
            character_name=character_name,
            story_prompt=story_prompt,
            setting=setting,
            art_style=art_style,
        )
        try:
            result = await self._call_gemini_structured(
                model=settings.OUTLINE_MODEL,
                prompt=prompt,
                response_schema=CharacterSheet,
            )
            if isinstance(result, CharacterSheet):
                return result
            return CharacterSheet.model_validate(result)
        except Exception as err:
            logger.error(f"Character sheet generation failed: {err}")
            if not isinstance(err, GenerationException):
                raise GenerationException(
                    f"Failed to generate character sheet: {err}",
                    code="CHARACTER_GENERATION_FAILED",
                ) from err
            raise

    async def generate_comic_script(
        self,
        story_prompt: str,
        character_sheet: CharacterSheet,
        setting: str,
        tone: str,
        art_style: str,
        custom_setting: str | None = None,
    ) -> ComicScriptSchema:
        """Generate a complete 5-panel comic story outline, dialogue, and image prompts."""
        prompt = build_comic_script_prompt(
            story_prompt=story_prompt,
            character_sheet=character_sheet,
            setting=setting,
            tone=tone,
            art_style=art_style,
            custom_setting=custom_setting,
        )
        try:
            result = await self._call_gemini_structured(
                model=settings.STORY_MODEL,
                prompt=prompt,
                response_schema=ComicScriptSchema,
            )
            if isinstance(result, ComicScriptSchema):
                return result
            return ComicScriptSchema.model_validate(result)
        except Exception as err:
            logger.error(f"Comic script generation failed: {err}")
            if not isinstance(err, GenerationException):
                raise GenerationException(
                    f"Failed to generate comic script: {err}",
                    code="SCRIPT_GENERATION_FAILED",
                ) from err
            raise

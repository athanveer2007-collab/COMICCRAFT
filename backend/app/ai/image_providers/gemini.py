"""Gemini / Imagen 3 implementation of ImageProvider."""

import io

from google import genai
from google.genai import types
from google.genai.errors import APIError
from PIL import Image
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from app.ai.image_providers.base import ImageProvider
from app.core.config import settings
from app.core.errors import GenerationException
from app.core.logging import get_logger

logger = get_logger(__name__)


class GeminiImageProvider(ImageProvider):
    """Generates comic panel artwork using Google Gen AI SDK (Imagen 3)."""

    def __init__(
        self,
        api_key: str | None = None,
        client: genai.Client | None = None,
        model_name: str | None = None,
    ) -> None:
        self.api_key = api_key or settings.GOOGLE_API_KEY
        self.model_name = model_name or settings.IMAGE_MODEL
        self.client = client or genai.Client(api_key=self.api_key)

    @retry(
        retry=retry_if_exception_type((APIError, ConnectionError, TimeoutError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(initial=1, max=8),
        reraise=True,
    )
    async def generate_panel_image(
        self,
        prompt: str,
        negative_prompt: str,
        reference_image: bytes | None = None,
        aspect_ratio: str = "4:3",
    ) -> bytes:
        """Generate panel illustration using Imagen 3 model via google-genai."""
        logger.info(f"Generating image with model [{self.model_name}] (ratio: {aspect_ratio})")

        config = types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio=aspect_ratio,
            negative_prompt=negative_prompt,
            output_mime_type="image/png",
        )

        try:
            response = await self.client.aio.models.generate_images(
                model=self.model_name,
                prompt=prompt,
                config=config,
            )

            if not response.generated_images:
                raise GenerationException(
                    "No images returned from Gemini image model.",
                    code="EMPTY_IMAGE_RESPONSE",
                )

            gen_img = response.generated_images[0]
            if gen_img.rai_filtered_reason:
                raise GenerationException(
                    f"Image generation blocked by safety filters: {gen_img.rai_filtered_reason}",
                    code="CONTENT_FILTERED",
                )

            if not gen_img.image or not gen_img.image.image_bytes:
                raise GenerationException(
                    "Generated image payload contains no bytes.",
                    code="MALFORMED_IMAGE_RESPONSE",
                )

            # Ensure valid PNG bytes
            img_bytes = gen_img.image.image_bytes
            with Image.open(io.BytesIO(img_bytes)) as pil_img:
                out_buffer = io.BytesIO()
                pil_img.save(out_buffer, format="PNG")
                return out_buffer.getvalue()

        except GenerationException:
            raise
        except APIError as api_err:
            logger.error(f"Gemini image generation API error: {api_err}")
            raise
        except Exception as exc:
            logger.error(f"Unexpected image generation failure: {exc}")
            raise GenerationException(
                f"Failed to generate panel image: {exc}",
                code="IMAGE_GENERATION_FAILED",
            ) from exc

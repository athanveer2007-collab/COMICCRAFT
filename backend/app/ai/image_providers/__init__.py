"""Image provider factory and public exports."""

from app.ai.image_providers.base import ImageProvider
from app.ai.image_providers.diffusers import DiffusersImageProvider
from app.ai.image_providers.gemini import GeminiImageProvider
from app.core.config import settings


def get_image_provider(provider_type: str | None = None) -> ImageProvider:
    """Factory creating configured ImageProvider instance."""
    provider = (provider_type or settings.IMAGE_PROVIDER).lower().strip()

    if provider == "diffusers":
        return DiffusersImageProvider()

    # Default to Gemini Imagen
    return GeminiImageProvider()


__all__ = [
    "ImageProvider",
    "GeminiImageProvider",
    "DiffusersImageProvider",
    "get_image_provider",
]

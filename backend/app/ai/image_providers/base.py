"""Base abstract class for AI Image Providers."""

from abc import ABC, abstractmethod


class ImageProvider(ABC):
    """Abstract interface defining the contract for comic panel image generation."""

    @abstractmethod
    async def generate_panel_image(
        self,
        prompt: str,
        negative_prompt: str,
        reference_image: bytes | None = None,
        aspect_ratio: str = "4:3",
    ) -> bytes:
        """Generate a single comic panel illustration and return raw PNG bytes."""
        pass

"""Hugging Face Diffusers / Self-Hosted implementation of ImageProvider."""

import io

from PIL import Image, ImageDraw

from app.ai.image_providers.base import ImageProvider
from app.core.logging import get_logger

logger = get_logger(__name__)


class DiffusersImageProvider(ImageProvider):
    """Generates images using Hugging Face Diffusers pipeline or local fallback."""

    def __init__(self, model_id: str = "stabilityai/stable-diffusion-xl-base-1.0") -> None:
        self.model_id = model_id
        self._pipeline = None
        self._init_pipeline()

    def _init_pipeline(self) -> None:
        """Attempt to load PyTorch Diffusers pipeline if dependencies are present."""
        try:
            import importlib

            torch = importlib.import_module("torch")
            diffusers = importlib.import_module("diffusers")
            auto_pipe = diffusers.AutoPipelineForText2Image

            device = "cuda" if torch.cuda.is_available() else "cpu"
            dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            logger.info(f"Loading Diffusers pipeline [{self.model_id}] on device [{device}]")
            self._pipeline = auto_pipe.from_pretrained(
                self.model_id,
                torch_dtype=dtype,
            ).to(device)
        except Exception as exc:
            logger.info(
                f"Diffusers/PyTorch not installed or accelerator unavailable ({exc}). "
                "Using synthetic high-resolution illustration fallback."
            )
            self._pipeline = None

    async def generate_panel_image(
        self,
        prompt: str,
        negative_prompt: str,
        reference_image: bytes | None = None,
        aspect_ratio: str = "4:3",
    ) -> bytes:
        """Generate panel illustration via Diffusers pipeline or deterministic fallback."""
        if self._pipeline is not None:
            try:
                result = self._pipeline(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    num_inference_steps=25,
                )
                pil_image: Image.Image = result.images[0]
                buf = io.BytesIO()
                pil_image.save(buf, format="PNG")
                return buf.getvalue()
            except Exception as e:
                logger.error(f"Diffusers execution failed: {e}. Falling back to canvas renderer.")

        # High-resolution stylized canvas fallback (800x600 for 4:3)
        width, height = (800, 600)
        img = Image.new("RGB", (width, height), color=(15, 23, 42))  # slate-900
        draw = ImageDraw.Draw(img)

        # Draw decorative comic frame border
        draw.rectangle((16, 16, width - 16, height - 16), outline=(99, 102, 241), width=4)
        draw.rectangle((24, 24, width - 24, height - 24), outline=(244, 63, 94), width=2)

        # Draw diagonal accent gradient stripes
        for i in range(0, width, 40):
            draw.line([(i, 28), (i + 120, height - 28)], fill=(30, 41, 59), width=2)

        # Header watermark
        draw.text(
            (40, 40),
            "COMICCRAFT ILLUSTRATION",
            fill=(248, 250, 252),
        )

        # Summary of prompt snippet
        snippet = prompt[:180] + ("..." if len(prompt) > 180 else "")
        draw.text(
            (40, height - 80),
            snippet,
            fill=(148, 163, 184),
        )

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

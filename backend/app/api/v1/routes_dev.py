"""Development-only endpoints, strictly disabled in production."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.config import settings

router = APIRouter(prefix="/dev", tags=["Development"])


class DevTestImageRequest(BaseModel):
    prompt: str = Field(..., description="Prompt to test image generation with")


class DevTestImageResponse(BaseModel):
    message: str
    prompt: str


@router.post("/test-image", response_model=DevTestImageResponse)
async def dev_test_image(payload: DevTestImageRequest) -> DevTestImageResponse:
    """Test image generation endpoint for developers. Blocked in production."""
    if settings.ENVIRONMENT.lower() == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Development endpoints are disabled in production environment.",
        )
    return DevTestImageResponse(
        message="Dev image endpoint ready (mock check)",
        prompt=payload.prompt,
    )

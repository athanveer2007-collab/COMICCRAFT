"""Common schemas used across ComicCraft backend."""

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Standardized error envelope payload."""

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error description")
    request_id: str = Field(..., description="Traceable request correlation ID")


class ErrorResponse(BaseModel):
    """Top-level error response model."""

    error: ErrorDetail


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(default="ok", description="Overall service status")
    version: str = Field(default="0.1.0", description="API version")
    environment: str = Field(..., description="Current environment")
    storage_writable: bool = Field(..., description="Indicates if storage directory is writable")

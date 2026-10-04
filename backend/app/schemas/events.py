"""Schemas for Server-Sent Events (SSE) progress streaming."""

from typing import Any

from pydantic import BaseModel


class ComicEvent(BaseModel):
    """Server-Sent Event payload broadcasted to clients during generation."""

    stage: str
    progress: int
    message: str
    comic_id: str
    job_id: str
    panel_index: int | None = None
    panel_data: dict[str, Any] | None = None
    error: str | None = None

    def to_sse(self) -> str:
        """Format as an SSE message block."""
        return f"event: {self.stage}\ndata: {self.model_dump_json()}\n\n"

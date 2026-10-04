"""Schemas for Job tracking and async status."""

from datetime import datetime

from pydantic import BaseModel


class JobCreateResponse(BaseModel):
    """Initial response returned upon POST /api/v1/comics."""

    job_id: str
    comic_id: str
    status: str
    stage: str


class JobResponse(BaseModel):
    """Detailed job status response."""

    id: str
    comic_id: str
    stage: str
    progress: int
    status: str
    error_code: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

"""SQLAlchemy ORM models for Comic and Job entities."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class ComicModel(Base):
    """Database model for Comic entity."""

    __tablename__ = "comics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    character_name: Mapped[str] = mapped_column(String(100), nullable=False)
    setting: Mapped[str] = mapped_column(String(100), nullable=False)
    custom_setting: Mapped[str | None] = mapped_column(String(200), nullable=True)
    tone: Mapped[str] = mapped_column(String(50), nullable=False)
    art_style: Mapped[str] = mapped_column(String(50), nullable=False)

    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    synopsis: Mapped[str | None] = mapped_column(Text, nullable=True)
    character_sheet: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    status: Mapped[str] = mapped_column(String(30), default="queued", nullable=False)
    panels: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)
    pdf_path: Mapped[str | None] = mapped_column(String(300), nullable=True)

    error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    jobs: Mapped[list["JobModel"]] = relationship(
        "JobModel", back_populates="comic", cascade="all, delete-orphan"
    )


class JobModel(Base):
    """Database model for asynchronous Comic Generation Job."""

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    comic_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("comics.id", ondelete="CASCADE"), index=True, nullable=False
    )
    stage: Mapped[str] = mapped_column(String(50), default="queued", nullable=False)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="in_progress", nullable=False)

    error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    comic: Mapped[ComicModel] = relationship("ComicModel", back_populates="jobs")

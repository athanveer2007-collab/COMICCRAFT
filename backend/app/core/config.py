"""Application configuration loaded from environment variables."""

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for ComicCraft backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment
    ENVIRONMENT: str = Field(default="development", description="Runtime environment")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")

    # AI Configuration
    GOOGLE_API_KEY: str = Field(default="", description="Google Gemini API key")
    OUTLINE_MODEL: str = Field(default="gemini-2.5-flash", description="Model for story outline")
    STORY_MODEL: str = Field(default="gemini-2.5-flash", description="Model for panel narration")
    IMAGE_MODEL: str = Field(
        default="imagen-3.0-generate-002", description="Model for image generation"
    )
    IMAGE_PROVIDER: str = Field(
        default="gemini", description="Image provider (gemini or diffusers)"
    )

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./comiccraft.db",
        description="Async database connection string",
    )

    # Storage
    STORAGE_DIR: str = Field(default="../storage", description="Local storage directory")

    # Concurrency and Rate Limiting
    IMAGE_CONCURRENCY_LIMIT: int = Field(default=3, description="Max concurrent image generations")
    RATE_LIMIT: str = Field(default="60/minute", description="API rate limit")

    # Security & CORS
    CORS_ORIGINS: str | list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
        description="Allowed CORS origins",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def storage_path(self) -> Path:
        """Resolved Path to the storage root."""
        return Path(self.STORAGE_DIR).resolve()

    @property
    def images_storage_path(self) -> Path:
        """Resolved Path to image storage."""
        p = self.storage_path / "images"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def pdfs_storage_path(self) -> Path:
        """Resolved Path to PDF storage."""
        p = self.storage_path / "pdfs"
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()

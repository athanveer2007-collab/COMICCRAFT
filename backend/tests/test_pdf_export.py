"""Tests for ReportLab PDF Exporter and PDF endpoints."""

from pathlib import Path

import pytest
from httpx import AsyncClient
from PIL import Image

from app.db.database import async_session_factory, init_db
from app.db.repositories import ComicRepository
from app.export.pdf_exporter import PDFExporter


def create_test_panel_image(dest: Path) -> None:
    """Create test PNG image on disk."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (400, 300), color=(99, 102, 241))
    img.save(dest, format="PNG")


@pytest.fixture(autouse=True)
async def setup_db() -> None:
    await init_db()


@pytest.fixture
def sample_pdf_panels(tmp_path: Path) -> tuple[list[dict], Path]:
    img_dir = tmp_path / "test_imgs"
    panels = []
    for i in range(1, 6):
        img_file = img_dir / f"panel_{i}.png"
        create_test_panel_image(img_file)
        panels.append(
            {
                "panel": i,
                "title": f"Panel {i} Awakening",
                "scene_description": f"The fox steps forward into radiant glowing moss in panel {i}.",
                "caption": f"Ancient secrets awaken in beat {i}.",
                "narration": f"Free felt the ground pulse with raw celestial rhythm {i}.",
                "dialogue": [
                    {"speaker": "Free", "text": f"We are close now in panel {i}."},
                    {"speaker": "Guardian", "text": "Step into the circle."},
                ],
                "image_prompt": f"Dramatic shot of Free the fox in panel {i}",
            }
        )
    return panels, img_dir


def test_pdf_exporter_creates_valid_pdf(
    tmp_path: Path, sample_pdf_panels: tuple[list[dict], Path]
) -> None:
    """Ensure PDFExporter creates a multi-page PDF starting with %PDF- header."""
    panels, img_dir = sample_pdf_panels
    exporter = PDFExporter(output_dir=tmp_path / "pdfs")

    pdf_file = exporter.generate_pdf(
        comic_id="test-comic-123",
        title="Chronicles of the Whisperwood",
        character_name="Free",
        setting="Enchanted Forest",
        tone="Dramatic",
        art_style="Anime",
        synopsis="A brave fox ventures into an ancient forest.",
        panels=panels,
        image_dir=img_dir,
    )

    assert pdf_file.exists()
    assert pdf_file.stat().st_size > 1000  # Multi-page PDF should be > 1KB
    header = pdf_file.read_bytes()[:5]
    assert header == b"%PDF-"


@pytest.mark.asyncio
async def test_export_and_download_endpoints(
    client: AsyncClient,
    tmp_path: Path,
    sample_pdf_panels: tuple[list[dict], Path],
) -> None:
    """Ensure POST /export generates PDF and GET /pdf downloads attachment."""
    panels, img_dir = sample_pdf_panels
    comic_id = "test-export-api"

    # Seed completed comic in DB
    async with async_session_factory() as session:
        repo = ComicRepository(session)
        _ = await repo.create(
            comic_id=comic_id,
            prompt="A story of a brave fox",
            character_name="Free",
            setting="Forest",
            tone="Dramatic",
            art_style="Anime",
        )
        await repo.update(
            comic_id,
            title="The Whisperwood Saga",
            synopsis="A journey into mystery",
            panels=panels,
            status="completed",
        )

    # Copy test images to storage dir
    from app.core.config import settings

    comic_storage_dir = settings.images_storage_path / comic_id
    comic_storage_dir.mkdir(parents=True, exist_ok=True)
    for i in range(1, 6):
        create_test_panel_image(comic_storage_dir / f"panel_{i}.png")

    # 1. Trigger export
    export_res = await client.post(f"/api/v1/comics/{comic_id}/export")
    assert export_res.status_code == 200
    export_data = export_res.json()
    assert export_data["pdf_url"] == f"/api/v1/comics/{comic_id}/pdf"

    # 2. Download PDF
    download_res = await client.get(f"/api/v1/comics/{comic_id}/pdf")
    assert download_res.status_code == 200
    assert download_res.headers["content-type"] == "application/pdf"
    assert "attachment" in download_res.headers.get("content-disposition", "")
    assert download_res.content[:5] == b"%PDF-"

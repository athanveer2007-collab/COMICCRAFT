"""Integration tests for Comics REST endpoints, asynchronous jobs, and SSE streaming."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.ai.schemas import CharacterSheet, ComicScriptSchema, DialogueItem, PanelSchema
from app.db.database import init_db
from app.services.generation_service import generation_service


@pytest.fixture(autouse=True)
async def initialize_test_database() -> None:
    """Ensure database schema is created before tests run."""
    await init_db()


@pytest.fixture
def mock_ai_script() -> ComicScriptSchema:
    char = CharacterSheet(
        name="Free",
        appearance="A brave fox with bright eyes",
        age_presentation="Young adult",
        hair="Russet fur",
        face="Sharp muzzle",
        eyes="Amber",
        outfit="Green cloak",
        primary_colors=["Orange", "Green"],
        accessories=["Leaf pin"],
        distinctive_features=["Ear notch"],
    )
    panels = [
        PanelSchema(
            panel=i,
            title=f"Panel {i} Title",
            scene_description=f"Scene {i} in the forest",
            caption=f"Caption {i}",
            narration=f"Narration {i}",
            dialogue=[DialogueItem(speaker="Free", text=f"Line {i}")],
            image_prompt=f"Image prompt for panel {i}",
        )
        for i in range(1, 6)
    ]
    return ComicScriptSchema(
        title="Chronicles of Free",
        synopsis="A brave fox explores a magical forest.",
        character_sheet=char,
        panels=panels,
    )


@pytest.mark.asyncio
async def test_create_comic_endpoint_validation_failure(client: AsyncClient) -> None:
    """Ensure POST /api/v1/comics fails with 422 on invalid/missing fields."""
    response = await client.post(
        "/api/v1/comics",
        json={"prompt": "short", "character_name": ""},
    )
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_create_comic_endpoint_success(
    client: AsyncClient, mock_ai_script: ComicScriptSchema
) -> None:
    """Ensure POST /api/v1/comics creates comic and job, returning 202 with job_id."""
    with (
        patch.object(
            generation_service.ai_service, "generate_character_sheet", new_callable=AsyncMock
        ) as mock_char,
        patch.object(
            generation_service.ai_service, "generate_comic_script", new_callable=AsyncMock
        ) as mock_script,
        patch.object(
            generation_service.character_service.provider,
            "generate_panel_image",
            new_callable=AsyncMock,
        ) as mock_img,
    ):
        mock_char.return_value = mock_ai_script.character_sheet
        mock_script.return_value = mock_ai_script
        mock_img.return_value = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDRdummy"

        payload = {
            "prompt": "A brave fox exploring an enchanted forest looking for ancient magic",
            "character_name": "Free",
            "setting": "Forest",
            "tone": "Dramatic",
            "art_style": "Anime",
        }

        response = await client.post("/api/v1/comics", json=payload)
        assert response.status_code == 202
        data = response.json()
        assert "job_id" in data
        assert "comic_id" in data
        assert data["status"] == "in_progress"

        comic_id = data["comic_id"]

        # Wait briefly for background generation task to complete
        await asyncio.sleep(0.5)

        # Verify GET /api/v1/comics/{id} returns created comic
        comic_res = await client.get(f"/api/v1/comics/{comic_id}")
        assert comic_res.status_code == 200
        comic_data = comic_res.json()
        assert comic_data["id"] == comic_id
        assert comic_data["character_name"] == "Free"
        assert comic_data["tone"] == "Dramatic"
        assert comic_data["art_style"] == "Anime"


@pytest.mark.asyncio
async def test_regenerate_comic_endpoint(
    client: AsyncClient, mock_ai_script: ComicScriptSchema
) -> None:
    """Ensure POST /api/v1/comics/{id}/regenerate updates tone/style and triggers new job."""
    with (
        patch.object(
            generation_service.ai_service, "generate_character_sheet", new_callable=AsyncMock
        ) as mock_char,
        patch.object(
            generation_service.ai_service, "generate_comic_script", new_callable=AsyncMock
        ) as mock_script,
        patch.object(
            generation_service.character_service.provider,
            "generate_panel_image",
            new_callable=AsyncMock,
        ) as mock_img,
    ):
        mock_char.return_value = mock_ai_script.character_sheet
        mock_script.return_value = mock_ai_script
        mock_img.return_value = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDRdummy"

        # Create initial comic
        create_res = await client.post(
            "/api/v1/comics",
            json={
                "prompt": "A brave fox exploring an enchanted forest looking for magic",
                "character_name": "Free",
                "setting": "Forest",
                "tone": "Dramatic",
                "art_style": "Anime",
            },
        )
        comic_id = create_res.json()["comic_id"]
        await asyncio.sleep(0.3)

        # Regenerate with Funny tone and Comic Book art style
        regen_res = await client.post(
            f"/api/v1/comics/{comic_id}/regenerate",
            json={"tone": "Funny", "art_style": "Comic Book"},
        )
        assert regen_res.status_code == 202
        regen_data = regen_res.json()
        assert regen_data["comic_id"] == comic_id
        assert "job_id" in regen_data

        await asyncio.sleep(0.3)

        # Check updated comic
        comic_res = await client.get(f"/api/v1/comics/{comic_id}")
        assert comic_res.status_code == 200
        comic_data = comic_res.json()
        assert comic_data["tone"] == "Funny"
        assert comic_data["art_style"] == "Comic Book"


@pytest.mark.asyncio
async def test_sse_event_broadcaster() -> None:
    """Ensure EventBroadcaster delivers events to subscribers."""
    from app.schemas.events import ComicEvent
    from app.services.job_service import broadcaster

    comic_id = "test-comic-sse"
    received_events = []

    async def subscriber_task() -> None:
        async for sse_msg in broadcaster.subscribe(comic_id):
            received_events.append(sse_msg)
            if "event: ready" in sse_msg:
                break

    task = asyncio.create_task(subscriber_task())
    await asyncio.sleep(0.05)  # Allow subscriber to attach

    # Broadcast outline event
    await broadcaster.broadcast(
        comic_id,
        ComicEvent(
            stage="outline",
            progress=20,
            message="Outline ready",
            comic_id=comic_id,
            job_id="job-1",
        ),
    )
    await asyncio.sleep(0.05)

    # Broadcast ready event
    await broadcaster.broadcast(
        comic_id,
        ComicEvent(
            stage="ready",
            progress=100,
            message="Comic ready",
            comic_id=comic_id,
            job_id="job-1",
        ),
    )

    await asyncio.wait_for(task, timeout=2.0)
    assert len(received_events) == 2
    assert "event: outline" in received_events[0]
    assert "event: ready" in received_events[1]

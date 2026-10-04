# ComicCraft API Reference

## 1. Overview & Conventions

The ComicCraft REST API allows clients to initiate comic generation jobs, monitor real-time generation progress via Server-Sent Events (SSE), retrieve finished comic data, trigger PDF compilation, and download the resulting documents.

- **Base URL**: `http://localhost:8000/api/v1`
- **Protocol**: HTTP/1.1 and Server-Sent Events (SSE)
- **Content Type**: `application/json; charset=utf-8`
- **Static Assets**: Panel illustrations are served statically from `/storage/images/{filename}`

---

## 2. Standard Error Response

All non-2xx responses return a consistent error object format:

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Comic e2e-comic-123 was not found.",
    "request_id": "4b68bb6e-e722-482f-8da7-951db1bc2e84"
  }
}
```

### Common Error Codes
| Code | HTTP Status | Description |
| :--- | :--- | :--- |
| `VALIDATION_ERROR` | 422 | Request body failed Pydantic or parameter validation. |
| `NOT_FOUND` | 404 | Comic record or referenced resource does not exist. |
| `RATE_LIMIT_EXCEEDED` | 429 | Rate limit exceeded. |
| `GENERATION_FAILED` | 500 | AI generation pipeline encountered a terminal error. |
| `PDF_EXPORT_FAILED` | 500 | ReportLab PDF compilation failed. |

---

## 3. Endpoints

### 3.1 Health Check
Checks service liveness, configuration, and storage write permissions.

```http
GET /api/v1/health
```

#### Response `200 OK`
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development",
  "storage_writable": true
}
```

---

### 3.2 Create Comic
Submits a prompt to start an asynchronous 5-panel comic generation job.

```http
POST /api/v1/comics
Content-Type: application/json
```

#### Request Body
```json
{
  "prompt": "A brave fox exploring an enchanted forest looking for star magic",
  "character_name": "Free",
  "setting": "Forest",
  "tone": "Dramatic",
  "art_style": "Anime"
}
```

#### Response `202 Accepted`
```json
{
  "job_id": "9bc1ae82-9f37-4d76-88b9-52e18587d609",
  "comic_id": "d0fbc497-2a62-42fe-b5bb-4f4094a48dc7",
  "status": "in_progress",
  "stage": "queued"
}
```

---

### 3.3 Get Comic Details
Retrieves comic metadata, character sheet, status, and all 5 generated panels.

```http
GET /api/v1/comics/{id}
```

#### Response `200 OK`
```json
{
  "id": "d0fbc497-2a62-42fe-b5bb-4f4094a48dc7",
  "prompt": "A brave fox exploring an enchanted forest...",
  "character_name": "Free",
  "setting": "Forest",
  "tone": "Dramatic",
  "art_style": "Anime",
  "title": "Chronicles of the Whisperwood",
  "synopsis": "Free travels through ancient ruins to restore the constellation bridge.",
  "status": "completed",
  "character_sheet": {
    "name": "Free",
    "appearance": "Brave young fox with amber eyes and swift footing",
    "age_presentation": "Young adult",
    "hair": "Russet fur",
    "face": "Pointed muzzle",
    "eyes": "Amber-gold",
    "outfit": "Green traveler's cloak with silver clasp",
    "primary_colors": ["Orange", "Green"],
    "accessories": ["Ancient star map"],
    "distinctive_features": ["Notch on left ear"]
  },
  "panels": [
    {
      "panel": 1,
      "title": "The Ancient Threshold",
      "scene_description": "Free stands at the glowing tree boundary.",
      "caption": "A whisper echoes from deep roots.",
      "narration": "Free paused at the boundary line.",
      "dialogue": [
        {
          "speaker": "Free",
          "text": "The journey begins."
        }
      ],
      "image_prompt": "Free the fox at enchanted tree entrance...",
      "image_url": "/storage/images/d0fbc497_panel_1.png"
    }
  ],
  "pdf_path": "storage/pdfs/d0fbc497_story.pdf",
  "created_at": "2026-10-04T12:00:00Z",
  "updated_at": "2026-10-04T12:02:15Z"
}
```

---

### 3.4 Live Generation Progress (Server-Sent Events)
Streams real-time generation milestones to the frontend.

```http
GET /api/v1/comics/{id}/events
Accept: text/event-stream
```

#### Event Lifecycle Sequence
1. `queued`: Generation queued in worker pool.
2. `outline`: AI creating structured character sheet and story outline.
3. `story`: 5-panel script, narration, and dialogue generated.
4. `images`: Beginning bounded concurrent illustration rendering.
5. `image_panel_1` ... `image_panel_5`: Emitted individually as each panel completes.
6. `layout`: ReportLab assembling multi-page PDF document.
7. `ready`: Comic generation fully complete.
8. `failed`: Emitted on error with diagnostic message.

#### SSE Wire Format Example
```text
event: outline
data: {"comic_id": "d0fbc497", "stage": "outline", "progress": 20, "message": "Synthesizing character sheet..."}

event: story
data: {"comic_id": "d0fbc497", "stage": "story", "progress": 40, "message": "Drafting 5-panel narrative and dialogue..."}

event: ready
data: {"comic_id": "d0fbc497", "stage": "ready", "progress": 100, "message": "Comic generated successfully!"}
```

---

### 3.5 Regenerate Comic
Regenerates an existing comic with updated tone and/or art style, creating new narrative dialogue and illustrations.

```http
POST /api/v1/comics/{id}/regenerate
Content-Type: application/json
```

#### Request Body
```json
{
  "tone": "Funny",
  "art_style": "Comic Book"
}
```

#### Response `202 Accepted`
```json
{
  "job_id": "782ef99a-8f92-4f96-857a-0da70891d418",
  "comic_id": "d0fbc497-2a62-42fe-b5bb-4f4094a48dc7",
  "status": "in_progress",
  "stage": "queued"
}
```

---

### 3.6 Export PDF
Manually triggers or recompiles the ReportLab PDF document for a completed comic.

```http
POST /api/v1/comics/{id}/export
```

#### Response `200 OK`
```json
{
  "pdf_url": "/api/v1/comics/d0fbc497-2a62-42fe-b5bb-4f4094a48dc7/pdf",
  "message": "PDF compiled successfully."
}
```

---

### 3.7 Download PDF
Downloads the generated PDF document.

```http
GET /api/v1/comics/{id}/pdf
```

#### Response `200 OK`
- `Content-Type`: `application/pdf`
- `Content-Disposition`: `attachment; filename="comic_d0fbc497_story.pdf"`
- Binary PDF stream.

---

### 3.8 Development Test Image
Generates a test image using the active image provider to verify provider credentials and rendering.

```http
POST /api/v1/dev/test-image
Content-Type: application/json
```

#### Request Body
```json
{
  "prompt": "A cute red fox in an anime forest",
  "negative_prompt": "blurry, low quality"
}
```

#### Response `200 OK`
- Returns image binary stream (`image/png`).

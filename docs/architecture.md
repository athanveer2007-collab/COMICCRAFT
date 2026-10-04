# ComicCraft System Architecture

## 1. Executive Overview

ComicCraft is a production-grade, asynchronous AI comic generator that transforms high-level narrative prompts into fully illustrated, 5-panel digital comic strips complete with dialogue, narration, sound effects, character sheets, and exportable print-ready multi-page PDFs.

The application follows an asynchronous event-driven monorepo architecture:
- **Backend**: Python 3.12+ FastAPI application utilizing SQLite with SQLAlchemy 2.0 asynchronous ORM, `google-genai` SDK with strict structured JSON schemas, bounded semaphore concurrency, pub-sub SSE streaming, and ReportLab PDF compilation.
- **Frontend**: React 19 single-page application built on Vite, TypeScript strict mode, Tailwind CSS v4, TanStack Query, and React Hook Form with real-time SSE progress tracking.

---

## 2. High-Level Architecture Diagram

```mermaid
flowchart TD
    subgraph Client["Frontend SPA (React 19 + TypeScript + Tailwind v4)"]
        UI_Form["Comic Creation Form (Zod + React Hook Form)"]
        UI_Stepper["Live SSE Progress Stepper (aria-live)"]
        UI_Preview["5-Panel Reader & Dialogue Bubbles"]
        UI_Export["PDF Export / Download Trigger"]
    end

    subgraph Gateway["FastAPI API Gateway (v1)"]
        Router_Comics["/api/v1/comics (CRUD, Regenerate, Export)"]
        Router_SSE["/api/v1/comics/{id}/events (Server-Sent Events)"]
        Router_PDF["/api/v1/comics/{id}/pdf (Direct File Stream)"]
        Router_Health["/api/v1/health (Liveness & Storage Check)"]
    end

    subgraph JobEngine["Background Job & Event Engine"]
        JobService["JobService (State & Transition Tracker)"]
        EventBroadcaster["EventBroadcaster (Asyncio In-Memory Pub/Sub)"]
        GenPipeline["Generation Pipeline Runner"]
    end

    subgraph AIService["AI & Character Consistency Engine"]
        GeminiClient["GeminiAIService (google-genai v2)"]
        CharSheetGen["Character Sheet Synthesizer"]
        ScriptGen["5-Panel Script Generator (Structured Schema)"]
        ImagePool["Bounded Concurrency Pool (asyncio.Semaphore)"]
        ImgProvider["ImageProvider (Gemini / Diffusers)"]
    end

    subgraph Persistence["Storage & Database"]
        DB[(SQLite via SQLAlchemy 2.0 Async + aiosqlite)]
        ImgDisk["/storage/images/{comic_id}_panel_{i}.png"]
        PDFDisk["/storage/pdfs/{comic_id}_story.pdf"]
    end

    UI_Form -->|POST /api/v1/comics| Router_Comics
    Router_Comics -->|Create Comic & Job| DB
    Router_Comics -->|Dispatch Background Task| GenPipeline
    UI_Stepper -->|GET /api/v1/comics/{id}/events| Router_SSE
    Router_SSE <--> EventBroadcaster

    GenPipeline --> JobService
    JobService --> DB
    JobService --> EventBroadcaster

    GenPipeline --> CharSheetGen
    CharSheetGen --> GeminiClient
    GenPipeline --> ScriptGen
    ScriptGen --> GeminiClient

    GenPipeline --> ImagePool
    ImagePool --> ImgProvider
    ImgProvider -->|Write Images| ImgDisk

    GenPipeline -->|Compile Multi-Page Document| PDFExporter["ReportLab PDF Exporter"]
    PDFExporter -->|Write PDF| PDFDisk

    UI_Preview -->|GET /api/v1/comics/{id}| Router_Comics
    UI_Export -->|POST /api/v1/comics/{id}/export| Router_Comics
    UI_Export -->|GET /api/v1/comics/{id}/pdf| Router_PDF
```

---

## 3. Core Subsystems

### 3.1 AI Generation & Structured Output
- **Model Integration**: Uses the official `google-genai` SDK (`gemini-2.5-flash` or configurable model IDs).
- **Structured Output**: Strictly enforced through Pydantic V2 schemas (`CharacterSheet`, `ComicScriptSchema`). No regex JSON stripping or markdown backtick parsing is used.
- **Strict Panel Validation**: Validates that output contains exactly five panels with sequential indexing (`1` through `5`), complete with `title`, `scene_description`, `caption`, `narration`, `dialogue`, and `image_prompt`.
- **Tenacity Retries**: Automatic retries with exponential backoff on transient network faults, rate limits, or validation anomalies.

### 3.2 Character Consistency Strategy
1. **Canonical Character Sheet**: Before any illustrations are prompted, the AI synthesizes an explicit visual breakdown containing:
   - Physical appearance, facial structure, eye color, fur/hair texture, clothing palette, accessories, and distinctive features.
2. **Prompt Injection**: Every panel prompt incorporates both the scene context and the explicit character sheet descriptor tags.
3. **Negative Prompting**: Injected into all image prompts to suppress common generation artifacts (e.g., extra limbs, distorted hands, duplicate characters, stray watermarks).
4. **Visual Seed Reference**: Where supported by the provider, the rendered output of Panel 1 is fed into panels 2–5 as a visual reference point.

### 3.3 Image Provider Abstraction
The backend implements an open/closed provider architecture:
```python
class ImageProvider(ABC):
    @abstractmethod
    async def generate_panel_image(
        self,
        prompt: str,
        negative_prompt: str | None = None,
        reference_image_bytes: bytes | None = None,
    ) -> bytes: ...
```
- **GeminiImageProvider**: Uses Imagen 3 via `google-genai` (`client.aio.models.generate_images`).
- **DiffusersImageProvider**: Uses local HuggingFace `diffusers` pipelines with intelligent fallback to clean canvas generation if GPU/weights are unavailable.
- **Concurrency Bounding**: Uses `asyncio.Semaphore(max_concurrency)` to prevent rate limit starvation or memory exhaustion during 5-panel parallel generation.

### 3.4 Asynchronous Job & SSE Streaming System
1. **Immediate Non-blocking Return**: `POST /api/v1/comics` validates input, stores pending records, launches `asyncio.create_task`, and returns `202 Accepted` with `job_id` and `comic_id` in < 50ms.
2. **Event Pub-Sub**: `EventBroadcaster` manages asynchronous FIFO queues per comic ID.
3. **SSE Lifecycle**:
   - `queued` $\rightarrow$ `outline` $\rightarrow$ `story` $\rightarrow$ `images` $\rightarrow$ `image_panel_1..5` $\rightarrow$ `layout` $\rightarrow$ `ready` (or `failed`).
4. **Heartbeat Keep-Alive**: Background ping comments (`: ping`) are pushed every 15s to keep connections alive through HTTP proxies.

### 3.5 PDF Compilation Subsystem
- **Engine**: ReportLab document builder (`SimpleDocTemplate`).
- **Structure**:
  - **Cover Page**: Styled banner, comic title, metadata table (Prompt, Character, Setting, Tone, Art Style, Date).
  - **Panels 1–5**: One panel per page. High-resolution centered illustration, panel title banner, scene narration box, speech dialogue bubbles with speaker callouts, and mood captions.
- **Safety**: Robust path traversal protection using normalized paths within configured storage directories.

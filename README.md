# COMICCRAFT — Production-Grade AI Comic Generator

[![CI](https://github.com/example/comiccraft/actions/workflows/ci.yml/badge.svg)](https://github.com/example/comiccraft/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![React 19](https://img.shields.io/badge/react-19-61dafb.svg)](https://react.dev/)

ComicCraft is a production-quality, asynchronous full-stack web application that transforms user prompts into coherent, beautifully illustrated 5-panel comic strips. It features real-time generation progress via Server-Sent Events (SSE), persistent character consistency, and downloadable print-ready multi-page PDFs compiled with ReportLab.

---

## Table of Contents
- [1. Overview & Key Capabilities](#1-overview--key-capabilities)
- [2. System Architecture](#2-system-architecture)
- [3. Prerequisites](#3-prerequisites)
- [4. Installation & Setup](#4-installation--setup)
- [5. Environment Configuration](#5-environment-configuration)
- [6. Gemini & Image Provider Configuration](#6-gemini--image-provider-configuration)
- [7. Local Development](#7-local-development)
- [8. Docker Deployment](#8-docker-deployment)
- [9. Testing & Quality Assurance](#9-testing--quality-assurance)
- [10. API Reference Overview](#10-api-reference-overview)
- [11. Troubleshooting](#11-troubleshooting)

---

## 1. Overview & Key Capabilities

- **Strict 5-Panel Structure**: Enforces narrative storytelling across 5 structured beats (Introduction, Inciting Incident, Rising Action, Climax, Resolution).
- **Character Consistency Engine**: Generates a detailed character sheet prior to panel generation, which is injected into all panel prompts alongside negative prompt filters and Panel 1 image reference chaining.
- **Tone & Style Presets**: Built-in visual and narrative presets:
  - **Settings**: School, Forest, Space, City, Custom
  - **Tones**: Light-hearted, Dramatic, Poetic, Funny
  - **Art Styles**: Anime, Pixel Art, Comic Book, Realistic
- **Live SSE Progress**: Real-time progress updates via Server-Sent Events with accessible `aria-live` screen reader notifications (no simulated timer progress).
- **Interactive Comic Reader**: Read finished comics with title, caption, narration, speech bubbles, and responsive panel viewports.
- **Regeneration**: Modify tone or style without losing the core premise, triggering re-writes and new illustrations.
- **Publication-Ready PDF Export**: Generates professional multi-page PDFs using ReportLab, complete with a title cover page, character sheet summary, panel artwork, captions, narration, and speech bubbles.

---

## 2. System Architecture

```text
comiccraft/
├── backend/                  # Python 3.12+ FastAPI backend
│   ├── app/
│   │   ├── ai/               # Gemini AI & Image provider implementations
│   │   ├── api/v1/           # REST & SSE endpoints (/comics, /export, /pdf, /health)
│   │   ├── core/             # Configuration, logging, errors, security
│   │   ├── db/               # SQLAlchemy 2.0 Async engine, models, repositories
│   │   ├── export/           # ReportLab multi-page PDF compiler
│   │   ├── schemas/          # Pydantic v2 domain schemas
│   │   └── services/         # Comic, Job, Character, and Generation services
│   ├── tests/                # 100% offline, deterministic Pytest suite
│   ├── storage/              # SQLite database, generated images & PDFs
│   ├── pyproject.toml        # Backend dependencies & tool config (uv/ruff/mypy)
│   └── Dockerfile            # Multi-stage production container
│
├── frontend/                 # React 19 Single Page Application
│   ├── src/
│   │   ├── api/              # Strongly typed API client & OpenAPI schemas
│   │   ├── components/       # UI components (cards, navbar, panels, steppers)
│   │   ├── hooks/            # SSE event hooks (useComicEvents)
│   │   └── pages/            # CreatePage, GeneratingPage, PreviewPage, ExportSuccessPage
│   ├── tests/                # Vitest & React Testing Library suite
│   ├── e2e/                  # Playwright end-to-end integration tests
│   ├── package.json          # Vite, Tailwind CSS v4, TanStack Query, React Hook Form
│   └── Dockerfile            # Multi-stage production container
│
├── docs/                     # Detailed architectural, API, and dev documentation
│   ├── architecture.md
│   ├── api.md
│   └── development.md
│
├── .github/workflows/        # GitHub Actions CI workflow
├── docker-compose.yml        # Orchestrates backend, frontend, and storage volumes
├── .env.example              # Template environment variables
└── README.md
```

For in-depth architectural specifications and diagrams, see [docs/architecture.md](docs/architecture.md).

---

## 3. Prerequisites

- **Python**: `3.12+`
- **Node.js**: `20.x` or `22.x LTS`
- **uv** (recommended) or `pip`
- **Docker & Docker Compose** (optional for containerized deployment)

---

## 4. Installation & Setup

### Clone the repository
```bash
git clone https://github.com/your-username/comiccraft.git
cd comiccraft
```

### Configure environment
```bash
cp .env.example .env
```
*(Populate your `GOOGLE_API_KEY` in `.env`)*

### Backend setup
```bash
cd backend
python -m venv .venv

# Activate on Windows
.venv\Scripts\activate
# Activate on macOS/Linux
source .venv/bin/activate

# Install dependencies
uv pip install -e ".[dev]"
# Or: pip install -e ".[dev]"
```

### Frontend setup
```bash
cd ../frontend
npm install
```

---

## 5. Environment Configuration

Supported configuration options in `.env`:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `GOOGLE_API_KEY` | *(None)* | Google Gemini API key (required for live generation). |
| `OUTLINE_MODEL` | `gemini-2.5-flash` | Gemini model for character sheet and story outline. |
| `STORY_MODEL` | `gemini-2.5-flash` | Gemini model for 5-panel dialogue and narrative scripting. |
| `IMAGE_MODEL` | `imagen-3.0-generate-002` | Google GenAI model used for panel illustrations. |
| `IMAGE_PROVIDER` | `gemini` | Image backend (`gemini` or `diffusers`). |
| `MAX_CONCURRENT_IMAGES` | `3` | Max concurrent image generation tasks (`asyncio.Semaphore`). |
| `DATABASE_URL` | `sqlite+aiosqlite:///./storage/comiccraft.db` | Async SQLite database connection string. |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Allowed CORS origins. |
| `STORAGE_DIR` | `./storage` | Directory where images and generated PDFs reside. |
| `ENVIRONMENT` | `development` | Deployment environment (`development` or `production`). |

---

## 6. Gemini & Image Provider Configuration

### Gemini AI Integration
ComicCraft uses the official Google Gen AI SDK (`google-genai` v2) with native asynchronous support:
- Uses `client.aio.models.generate_content` with strict response schemas (`response_schema=PydanticModel`).
- No raw string parsing or regex markdown removal is performed.

### Image Providers
- **Gemini (`IMAGE_PROVIDER=gemini`)**: Generates illustrations via Imagen 3 (`imagen-3.0-generate-002`).
- **Diffusers (`IMAGE_PROVIDER=diffusers`)**: Generates illustrations via HuggingFace diffusers with an intelligent offline canvas fallback.

---

## 7. Local Development

### Start Backend Dev Server
```bash
cd backend
.venv\Scripts\activate   # or source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- Interactive Swagger docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health check: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

### Start Frontend Dev Server
```bash
cd frontend
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 8. Docker Deployment

Deploy the entire stack with a single command:

```bash
docker compose up --build -d
```

- Frontend: [http://localhost:5173](http://localhost:5173)
- Backend: [http://localhost:8000](http://localhost:8000)
- OpenAPI Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

To stop the containers:
```bash
docker compose down
```

---

## 9. Testing & Quality Assurance

All automated tests are deterministic and run offline without requiring external API keys.

### Run Backend Tests, Linting & Typechecks
```bash
cd backend

# Pytest suite (24 tests covering AI, jobs, SSE, PDF export, providers)
pytest

# Code formatting and linting
ruff check .

# Static type analysis
mypy app
```

### Run Frontend Tests, Linting & E2E
```bash
cd frontend

# Component & Unit tests (Vitest)
npm run test

# Typecheck with TypeScript
npm run typecheck

# Lint with ESLint
npm run lint

# Production build check
npm run build

# End-to-End browser tests (Playwright)
npm run test:e2e
```

---

## 10. API Reference Overview

Detailed documentation available at [docs/api.md](docs/api.md).

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/comics` | Initiate asynchronous 5-panel comic generation job |
| `GET` | `/api/v1/comics/{id}` | Retrieve comic metadata, character sheet, and panels |
| `GET` | `/api/v1/comics/{id}/events` | Real-time Server-Sent Events (SSE) progress stream |
| `POST` | `/api/v1/comics/{id}/regenerate` | Regenerate comic with alternative tone/style presets |
| `POST` | `/api/v1/comics/{id}/export` | Compile or refresh ReportLab multi-page PDF |
| `GET` | `/api/v1/comics/{id}/pdf` | Stream compiled PDF file directly |
| `GET` | `/api/v1/health` | Service health, version, and storage writability |
| `POST` | `/api/v1/dev/test-image` | Development test endpoint for active image provider |

---

## 11. Troubleshooting

### 1. `google.genai.errors.APIError` or Rate Limits
- Ensure `GOOGLE_API_KEY` is set in `.env`.
- Bounded concurrency can be lowered by adjusting `MAX_CONCURRENT_IMAGES=1` or `2`.
- Automatic exponential backoff retries are configured via `tenacity`.

### 2. SQLite Database Locking
- Async SQLite requires `aiosqlite` and `greenlet`. Ensure both are installed:
  ```bash
  pip install aiosqlite greenlet
  ```

### 3. Server-Sent Events Disconnections
- The backend automatically emits `: ping` heartbeat comments every 15 seconds.
- The frontend `useComicEvents` hook contains automatic reconnection logic up to 5 attempts.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

# ComicCraft Development & Operations Guide

## 1. Prerequisites

Ensure the following tools are installed on your machine:
- **Python**: 3.12 or newer
- **Node.js**: 20+ or 22 LTS
- **uv** (recommended) or **pip**: For Python package management
- **Docker & Docker Compose**: For containerized deployment

---

## 2. Environment Configuration

1. Copy `.env.example` to `.env` in the project root:
   ```bash
   cp .env.example .env
   ```
2. Populate the environment variables:
   ```env
   # Google Gemini API Key
   GOOGLE_API_KEY=your_gemini_api_key_here

   # Model IDs (Supported by google-genai v2 SDK)
   OUTLINE_MODEL=gemini-2.5-flash
   STORY_MODEL=gemini-2.5-flash
   IMAGE_MODEL=imagen-3.0-generate-002

   # Image Provider (gemini or diffusers)
   IMAGE_PROVIDER=gemini

   # Database URL
   DATABASE_URL=sqlite+aiosqlite:///./storage/comiccraft.db

   # CORS Origins
   CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

   # Storage directory
   STORAGE_DIR=./storage

   # Max concurrent image generation tasks
   MAX_CONCURRENT_IMAGES=3

   ENVIRONMENT=development
   ```

---

## 3. Backend Setup & Local Development

### 3.1 Virtual Environment Installation
```bash
cd backend
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On Linux/macOS:
source .venv/bin/activate

# Install dependencies using uv or pip:
uv pip install -e ".[dev]"
```

### 3.2 Running the Backend Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- Swagger API Docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/api/v1/health`

### 3.3 Running Backend Quality Checks
```bash
# Run test suite (fully offline & mocked)
pytest

# Code linting & formatting checks
ruff check .
ruff format --check .

# Static type analysis
mypy app
```

---

## 4. Frontend Setup & Local Development

### 4.1 Install Node Dependencies
```bash
cd frontend
npm install
```

### 4.2 Run Frontend Development Server
```bash
npm run dev
```
Open `http://localhost:5173` in your browser.

### 4.3 Running Frontend Quality Checks
```bash
# Run unit & component tests
npm run test

# Typecheck with TypeScript
npm run typecheck

# Lint with ESLint
npm run lint

# Production build bundle
npm run build

# End-to-End browser tests (Playwright)
npm run test:e2e
```

---

## 5. Docker Deployment

To launch the complete application with backend, frontend, and persistent volumes:

```bash
# Build and run containers in detached mode
docker compose up --build -d

# Check service logs
docker compose logs -f

# Stop and remove containers
docker compose down
```

Services exposed:
- **Frontend SPA**: `http://localhost:5173` (or port 80 via nginx reverse proxy in production)
- **Backend API**: `http://localhost:8000`
- **Persistent storage**: Mounted at `./storage` for generated comic images and PDF documents.

---

## 6. Continuous Integration (CI)

GitHub Actions workflows are defined in `.github/workflows/ci.yml`:
- **Backend Pipeline**: Runs Ruff linting, Mypy strict typing, and full Pytest suite on Python 3.12.
- **Frontend Pipeline**: Runs ESLint, TypeScript compiler check (`tsc --noEmit`), Vitest test suite, and production Vite compilation.

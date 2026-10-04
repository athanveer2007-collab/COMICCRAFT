# ComicCraft — Production-Grade AI Comic Generator

ComicCraft is a full-stack, production-grade web application that transforms user prompts into coherent, illustrated 5-panel comics with real-time generation progress and professional PDF export.

## Architecture

- **Backend**: FastAPI, Python 3.12, SQLAlchemy 2.0 Async, SQLite, Google Gen AI SDK (`google-genai`), ReportLab, Tenacity.
- **Frontend**: React 19, TypeScript strict, Vite, Tailwind CSS v4, shadcn/ui, TanStack Query, React Hook Form, Zod.
- **Real-Time Communication**: Server-Sent Events (SSE).

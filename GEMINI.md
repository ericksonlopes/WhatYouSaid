# GEMINI Project Context: WhatYouSaid

## Project Overview
WhatYouSaid is a vectorized data hub designed for semantic search and Retrieval-Augmented Generation (RAG). It ingests content from YouTube videos (transcripts/audio), local files (PDF, DOCX, TXT, MP4), and web URLs (via Docling and Crawl4AI).

### Tech Stack
- **Backend**: Python 3.12, FastAPI, SQLAlchemy (relational DB), Redis (Task Queue & Event Bus), LangChain (RAG orchestration), WhisperX (Audio processing/Diarization).
- **Frontend**: React 19, Vite, Tailwind CSS 4, Lucide-React, i18next (Internationalization).
- **Infrastructure**: Support for SQLite, PostgreSQL, FAISS, Weaviate, ChromaDB, and Qdrant.

### Architecture
The project follows **Clean Architecture** principles:
- **Domain**: Entities and interfaces (interfaces for repositories, services, and extractors).
- **Application**: Use cases (e.g., `FileIngestionUseCase`, `SearchUseCase`) and worker logic.
- **Infrastructure**: Implementations of external services (Redis, S3/MinIO, specific Extractors).
- **Presentation**: FastAPI routes, schemas, and dependency injection layer (`dependencies.py`).

---

## Building and Running

### Prerequisites
- Python 3.12+ (managed via `uv` or `pip`)
- Node.js & npm (for frontend)
- Docker & Docker Compose (for infrastructure services)

### Key Commands

#### Infrastructure
```bash
docker-compose up -d  # Lite version (SQLite + FAISS + Redis)
docker-compose --profile base up -d  # Full version (Postgres + Weaviate + Redis)
```

#### Backend
```bash
uv sync  # Install dependencies
uv run main.py  # Start the API server
```

#### Frontend
```bash
cd frontend
npm install
npm run dev  # Start Vite development server
```

#### Quality & Testing
```bash
uv run pytest  # Run backend tests
uv run ruff check . --fix  # Linting and auto-fixing
uv run mypy .  # Static type checking
uv run bandit -r src/  # Security scan
```

---

## Development Conventions

### Coding Style
- **Python**: Strict adherence to `ruff` formatting and `mypy` type safety.
- **Frontend**: Functional components with Tailwind CSS utility classes. Support for EN/PT-BR via `i18next`.
- **Naming**: Snake_case for Python, camelCase for TypeScript/React.

### Dependency Injection
- Always use the dependency injection layer in `src/presentation/api/dependencies.py` to instantiate use cases. Avoid direct instantiation within router files to ensure testability.

### Background Processing
- Heavy tasks (audio processing, large file ingestion) must be enqueued via `RedisTaskQueueService`.
- Progress updates are communicated to the frontend in real-time using the **SSE (Server-Sent Events)** endpoint via the Redis Event Bus.

### Testing Mandates
- **Tests**: `pytest` is used for both unit and integration tests. New features must include corresponding test files in the `tests/` directory.
- **Mocking**: Infrastructure dependencies (like S3/MinIO) should be mocked in tests to avoid external connection requirements.

---

## Instruction Precedence
1. Instructions in specific task prompts.
2. Context found in `.gemini/gemini.md` (Global Mandates).
3. Conventions described in this `GEMINI.md` file.

# 🗺️ WhatYouSaid Agent Guide (Architecture & Workflows)

This document serves as the "Architectural Compass" for AI agents on the project.
- For specialized workflows (tests, commits, database), see the **Skills** in `.agents/skills/`.
- For step-by-step procedures (SOPs), see the **Workflows** in `.agents/workflows/`.

## 🏗️ Big Picture Architecture

### Purpose
`WhatYouSaid` is a person-centric vectorized data hub designed to extract, process, and index information from various sources (YouTube, Audio, Text) for semantic search and RAG.

### Project Structure
- `src/domain/`: Entities, Enums, and Interfaces (DDD).
- `src/application/`: Use Cases (Orchestration).
- `src/infrastructure/`: Concrete implementations (Extractors, SQL/Vector Repositories, LLM Services).
- `src/presentation/api/`: FastAPI Routes and Schemas.
- `frontend/`: React/TypeScript Dashboard.
- `tests/`: Mirrored structure of `src/`.

---

## 💻 Developer Workflows

### Quick Setup (Backend)
```bash
python -m venv .venv
.\.venv\Scripts\Activate
uv sync --group dev
python -m pip install -e .
uv run playwright install chromium
uv run crawl4ai-setup
```

### Quick Setup (Frontend)
```bash
cd frontend
npm install
npm run dev
```

### Infrastructure Commands
- **Migrations (Alembic)**: `alembic upgrade head`
- **Docker Compose**: `docker compose -f .devcontainer/docker-compose.yml up --build`
- **Testing (Pytest)**: `pytest`
- **Quality**: `ruff check . --fix`, `mypy .`, `bandit -r src/`

---

## 🎨 Frontend (React/TypeScript)

- **Entry point**: `frontend/src/App.tsx`.
- **State**: Managed via `AppContext` in `frontend/src/store/`.
- **Services**: API communication in `frontend/src/services/api.ts`.

---

## 🔧 Project Conventions

- **Environment Variables**: Double delimiter `__` for nested variables in Pydantic (e.g., `VECTOR__STORE_TYPE`).
- **Timezones**: Always use `datetime.now(timezone.utc)`.
- **Testing**: New files in `src/` require corresponding tests in `tests/` (see `secure-commit` Skill).

---

## 🧠 Integrations and LLMs
- **Vector Stores**: Native support for Weaviate and FAISS via `IVectorRepository`.
- **Embeddings**: Abstracted via `EmbeddingService`. Default models: `BAAI/bge-m3`.

---
*This guide must be kept up to date as the architecture evolves.*

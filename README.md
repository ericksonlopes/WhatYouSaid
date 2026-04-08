<div align="center">

# WhatYouSaid

## The Vectorized Intelligence & Diarization Hub


[![codecov](https://codecov.io/github/ericksonlopes/WhatYouSaid/branch/main/graph/badge.svg?token=8CZJARVJUE)](https://codecov.io/github/ericksonlopes/WhatYouSaid)
[![Tests](https://github.com/ericksonlopes/WhatYouSaid/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/ericksonlopes/WhatYouSaid/actions/workflows/tests.yml)
[![Code Quality](https://github.com/ericksonlopes/WhatYouSaid/actions/workflows/code-quality.yml/badge.svg?branch=main)](https://github.com/ericksonlopes/WhatYouSaid/actions/workflows/code-quality.yml)
[![Security](https://github.com/ericksonlopes/WhatYouSaid/actions/workflows/security.yml/badge.svg?branch=main)](https://github.com/ericksonlopes/WhatYouSaid/actions/workflows/security.yml)

![Python](https://img.shields.io/badge/-Python-3776AB?&logo=Python&logoColor=FFFFFF)
![React](https://img.shields.io/badge/-React-61DAFB?&logo=React&logoColor=000000)
![FastAPI](https://img.shields.io/badge/-FastAPI-05998B?&logo=FastAPI&logoColor=FFFFFF)
![Redis](https://img.shields.io/badge/-Redis-DC382D?&logo=Redis&logoColor=FFFFFF)
![Postgres](https://img.shields.io/badge/-PostgreSQL-4169E1?&logo=PostgreSQL&logoColor=FFFFFF)

</div>

**WhatYouSaid** is a state-of-the-art vectorized data hub designed to explore any knowledge domain. It transforms unstructured audio, video, files, and web content into structured, searchable intelligence using advanced AI techniques, including **Speaker Diarization**, **Voice Recognition**, and **RAG** (Retrieval-Augmented Generation).

---

## ✨ Features

### 🎧 Diarization & Voice Intelligence

- **Speaker Segmentation**: Automatically split audio/video files by speaker using WhisperX/Whisper for unmatched accuracy.
- **Voice Recognition**: Identify and label speakers across your entire knowledge base using trained voice profiles.
- **Diarization Pipeline**: Interactive dashboard to review, edit, and finalize transcripts and speaker assignments before indexing.


### 📥 Multi-Source Ingestion

- **YouTube Ecosystem**: Full support for individual videos, entire playlists, or entire channels.
- **Document Extractors**: High-fidelity extraction from PDF, DOCX, and TXT files.
- **Web Intelligence**: Powerful scraping via **Crawl4AI** and **Docling** for websites and remote URLs.
- **Robust Pipeline**: Step-by-step progress tracking with real-time SSE notifications and full rollback support on failure.

### 🔍 Advanced Semantic Search

- **Hybrid Search**: Combining Vector (FAISS/Weaviate/Chroma) and Keyword (BM25) search for maximum precision.
- **Re-Ranking**: Specialized Cross-Encoders ensure the most relevant context is always at the top.
- **Pluggable Architecture**: Seamlessly switch between SQL databases (SQLite/Postgres/MySQL) and Vector stores.

---

## 🚀 Quick Start

WhatYouSaid is powered by **Python 3.12** and uses **uv** for high-speed dependency management.

### 1. Prerequisites

- [uv](https://github.com/astral-sh/uv) (Recommended) or `pip`
- [Docker](https://www.docker.com/)

### 2. Environment Setup

```bash
# Clone the repository
git clone https://github.com/ericksonlopes/WhatYouSaid.git
cd WhatYouSaid

# Install dependencies (including dev groups)
uv sync --group dev
```

### 3. Spin Up Infrastructure

```bash
# Lite mode: SQLite + FAISS + Redis
docker-compose up -d

# Scalable mode: PostgreSQL + Weaviate + Redis
docker-compose --profile base up -d
```

### 4. Run Application

```bash
# Start Backend (FastAPI)
python main.py

# Start Frontend (React)
cd frontend
npm install
npm run dev
```

---

## 🐳 Deployment Profiles

We use **Docker Profiles** to keep your environment lean. Only the services you need are started.

| Component | Lite Profile (Default) | Scalable Profile (`base`) |
| :--- | :--- | :--- |
| **Relational DB** | SQLite (File-based) | PostgreSQL / MySQL / MariaDB |
| **Vector Store** | FAISS (Local) | Weaviate / ChromaDB / Qdrant |
| **Task Queue** | Redis | Redis (Production-ready) |

> [!TIP]
> Use the **Scalable** profile if you require high-concurrency access or plan to manage multi-gigabyte vector indexes.

---

## 🏗️ Clean Architecture

The system follows a modular approach ensuring maximum testability and maintainability:

- **Application Layer**: Orchestrates logic via use cases and resolves background worker dependencies through a `ServiceRegistry`.
- **Infrastructure Layer**:
  - `extractors/`: Fetch raw content from specialized sources (Docling, YouTube, Crawl4AI).
  - `repositories/`: Persistence via SQL (SQLAlchemy) and specialized Vector clients.
  - `services/`: Core providers for embeddings, text splitting, and re-ranking.
- **Presentation Layer**: FastAPI-based REST API with real-time event broadcasting and a modern React dashboard.

---

## 🤝 Contributing & Quality

Contributions are what make the open-source community such an amazing place! Please:

1. Open an **Issue** to discuss proposed changes.
2. Ensure `uv run ruff check . --fix` and `uv run mypy .` pass.
3. Run all tests: `uv run pytest`.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<div align="center">

Hand-crafted with ❤️ by **Erickson Lopes**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Erickson_Lopes-blue?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/ericksonlopes/)

</div>

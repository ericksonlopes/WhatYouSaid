## Description
The WhatYouSaid application currently has a significant resource footprint, with local development environments (like `.venv`, `node_modules`, and `.ms-playwright`) consuming over 7GB. The Docker images, particularly for the backend, are also quite large due to heavy dependencies like PyTorch, Playwright, and Docling. This issue aims to optimize the application's performance and size by implementing multi-stage Docker builds, refining dependency management, and optimizing frontend assets. These changes will make the application "lighter," faster to build/deploy, and more efficient in resource-constrained environments.

## Tasks

### Backend & Infrastructure
- [ ] **Multi-stage Docker Build (Backend)**: Implement a multi-stage build in `Dockerfile.backend` to separate the build environment from the runtime environment.
- [ ] **Minimize Playwright Footprint**: Configure Playwright to only install the Chromium browser with `--no-shell` or use a dedicated smaller playwright image. Explore using `playwright-python` instead of the full CLI if possible.
- [ ] **PyTorch Optimization**: Use the CPU-only version of PyTorch in the Docker image unless GPU support is explicitly requested, significantly reducing image size.
- [ ] **Dependency Cleanup**: Review `pyproject.toml` and move purely development/testing dependencies (like `pytest`, `ruff`, `mypy`) to the `[dependency-groups].dev` section.
- [ ] **Caching Strategies**: Optimize Docker layer caching by copying only `pyproject.toml` and `uv.lock` before installing dependencies.

### Frontend
- [ ] **Asset Compression**: Implement Gzip or Brotli compression for static assets in the Nginx configuration (`frontend/nginx.conf`).
- [ ] **Code Splitting**: Ensure Vite is configured to effectively split chunks to reduce the initial load size of the dashboard.
- [ ] **Image Optimization**: Audit and optimize any static images or icons used in the frontend.

### General
- [ ] **.dockerignore Audit**: Review and update `.dockerignore` to ensure large local directories like `.venv`, `node_modules`, and `.ms-playwright` are never copied into the build context.

## Additional Context
- Current local footprint: ~7.48GB.
- Main contributors to size: PyTorch, Playwright browsers, and `node_modules`.
- Tools to be used: Docker multi-stage builds, `uv` for efficient Python package management, Vite build optimizations.
- Reference: The project already uses `uv`, which is a great start for fast and efficient Python dependency management.

---
[Submit this issue to GitHub](https://github.com/ericksonlopes/WhatYouSaid/issues/new?title=chore:%20optimize%20application%20performance%20and%20resource%20footprint&body=Check%20details%20at%20docs/issues/optimize-performance-and-size.md)

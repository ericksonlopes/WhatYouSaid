---
description: How to create and apply database migrations with Alembic in WhatYouSaid
---

# 🗄️ Workflow: Database Migrations (Alembic)

This workflow ensures that database schema changes are made safely and traceably.

## 1. Model Modification
- [ ] Change or create the SQL models in `src/infrastructure/database/models.py`.
- [ ] Ensure the new model is discovered by `alembic/env.py` (import it explicitly if necessary).

## 2. Revision Generation
- [ ] Generate a new automatic revision:
    ```bash
    alembic revision --autogenerate -m "description_of_change"
    ```
- [ ] Inspect the generated file in `alembic/versions/` to ensure the `upgrade` and `downgrade` scripts are correct.

## 3. Applying the Change
- [ ] Apply the migration to the database:
    ```bash
    alembic upgrade head
    ```
- [ ] Verify that the schema updated correctly (e.g., `ls app.sqlite` or inspect with a DB tool).

## 4. Database Testing
- [ ] Run infrastructure tests to ensure that queries continue to work:
    ```bash
    pytest tests/infrastructure/database/
    ```

---
// turbo
## Quick Verification
Run `alembic current` to see the current database version.

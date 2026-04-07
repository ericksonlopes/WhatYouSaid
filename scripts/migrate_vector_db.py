"""
Script to migrate/re-ingest chunks into the configured vector database.
It reads the `chunk_index` records from the SQL database and pushes
them to the Vector Store, using the current embedding model.
This is useful when changing embedding models or vector databases.

NOTE: This script reuses the existing chunk IDs as vector document IDs.
Backends that do not upsert on insert (e.g. ChromaDB) may produce
duplicate-ID errors or silent duplicates if the target collection is
non-empty. Run `scripts/clear_vector_db.py` before this script to
ensure a clean migration.
"""

import os
import sys
import traceback
from datetime import datetime
from typing import cast, Dict, Any, Optional
from uuid import UUID

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from src.infrastructure.repositories.sql.connector import Session as DBSessionFactory
from src.infrastructure.repositories.sql.models.chunk_index import ChunkIndexModel
from src.infrastructure.services.model_loader_service import ModelLoaderService
from src.infrastructure.repositories.vector.models.chunk_model import ChunkModel
from src.config.settings import Settings
from src.config.logger import Logger
from src.presentation.api.dependencies import get_vector_repository

logger = Logger()


def migrate_vector_db(batch_size: int = 100) -> None:
    settings = Settings()

    embedding_model_name = settings.model_embedding.name
    logger.info(f"Initializing Model Loader Service with model: {embedding_model_name}")
    model_loader = ModelLoaderService(model_name=embedding_model_name)
    model_loader.load_model()

    logger.info("Initializing Vector Repository...")
    # This automatically instantiates the vector repo for the correct type defined in .env
    vector_repo = get_vector_repository(settings=settings, model_loader=model_loader)

    if not vector_repo.is_ready():
        logger.error("Vector Repository is not ready. Aborting.")
        sys.exit(1)

    db: Session = DBSessionFactory()
    try:
        total_migrated = 0
        last_created_at: Optional[datetime] = None
        last_id: Optional[UUID] = None

        while True:
            query = db.query(ChunkIndexModel).order_by(
                ChunkIndexModel.created_at, ChunkIndexModel.id
            )
            # Keyset pagination: skip rows already processed in previous batches
            if last_created_at is not None:
                query = query.filter(
                    or_(
                        ChunkIndexModel.created_at > last_created_at,
                        and_(
                            ChunkIndexModel.created_at == last_created_at,
                            ChunkIndexModel.id > last_id,
                        ),
                    )
                )

            chunk_models_sql = query.limit(batch_size).all()

            if not chunk_models_sql:
                break

            # Capture keyset cursors from the last row of this batch
            last_created_at = chunk_models_sql[-1].created_at
            last_id = chunk_models_sql[-1].id

            documents = []
            for chunk_sql in chunk_models_sql:
                extra_data: Dict[str, Any] = (
                    # Shallow copy is sufficient: we only add a top-level key below
                    dict(chunk_sql.extra)
                    if isinstance(chunk_sql.extra, dict)
                    else {}
                )
                if chunk_sql.vector_store_type:
                    extra_data["original_vector_store_type"] = (
                        chunk_sql.vector_store_type
                    )

                doc = ChunkModel(
                    id=cast(UUID, chunk_sql.id),
                    job_id=cast(UUID, chunk_sql.job_id),
                    content_source_id=cast(UUID, chunk_sql.content_source_id),
                    source_type=str(chunk_sql.source_type or "UNKNOWN"),
                    external_source=cast(str, chunk_sql.external_source),
                    subject_id=cast(UUID, chunk_sql.subject_id),
                    index=cast(int, chunk_sql.index),
                    content=cast(str, chunk_sql.content),
                    tokens_count=cast(int, chunk_sql.tokens_count),
                    language=cast(str, chunk_sql.language),
                    embedding_model=embedding_model_name,
                    created_at=cast(datetime, chunk_sql.created_at),
                    version_number=cast(int, chunk_sql.version_number),
                    extra=extra_data,
                )
                documents.append(doc)

            total_migrated += len(documents)
            logger.info(
                f"Uploading batch of {len(documents)} chunks to vector db... (Total migrated so far: {total_migrated})"
            )

            # create_documents will internally call the EmbeddingService for the texts and save them
            vector_repo.create_documents(documents)

            # Expunge all ORM objects to prevent unbounded memory growth
            db.expunge_all()

        logger.info(
            f"Vector DB migration finished successfully! Total chunks migrated: {total_migrated}"
        )

    except Exception as e:
        logger.error(f"Migration failed: {e}\n{traceback.format_exc()}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    migrate_vector_db()

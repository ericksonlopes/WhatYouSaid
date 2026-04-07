"""
Script to migrate/re-ingest chunks into the configured vector database.
It reads the `chunk_index` records from the SQL database and pushes
them to the Vector Store, using the current embedding model.
This is useful when changing embedding models or vector databases.
"""

import os
import sys
from datetime import datetime
from typing import cast, Dict, Any
from uuid import UUID

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
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
        total_chunks = db.query(ChunkIndexModel).count()
        logger.info(f"Total chunks to migrate: {total_chunks}")

        offset = 0
        while offset < total_chunks:
            chunk_models_sql = (
                db.query(ChunkIndexModel)
                .order_by(ChunkIndexModel.created_at)
                .offset(offset)
                .limit(batch_size)
                .all()
            )

            if not chunk_models_sql:
                break

            documents = []
            for chunk_sql in chunk_models_sql:
                extra_data = (
                    cast(Dict[str, Any], chunk_sql.extra)
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
                    created_at=cast(datetime, chunk_sql.created_at or datetime.now()),
                    version_number=cast(int, chunk_sql.version_number),
                    extra=extra_data,
                )
                documents.append(doc)

            logger.info(
                f"Uploading batch of {len(documents)} chunks to vector db... (Progress: {offset + len(documents)} / {total_chunks})"
            )

            # create_documents will internally call the EmbeddingService for the texts and save them
            vector_repo.create_documents(documents)

            offset += batch_size

        logger.info("Vector DB migration finished successfully!")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    migrate_vector_db()

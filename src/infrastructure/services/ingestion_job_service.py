from typing import Optional, List
from uuid import UUID

from src.config.logger import Logger
from src.domain.entities.enums.ingestion_job_status_enum import IngestionJobStatus
from src.domain.entities.ingestion_job_entity import IngestionJobEntity
from src.domain.mappers.ingestion_job_mapper import IngestionJobMapper
from src.infrastructure.repositories.sql.ingestion_job_repository import IngestionJobSQLRepository


class IngestionJobService:
    """Service layer for ingestion jobs."""

    def __init__(self, repository: IngestionJobSQLRepository, logger: Optional[Logger] = None) -> None:
        self._repo = repository
        self._logger = logger or Logger()

    def create_job(self, content_source_id: Optional[UUID], status: IngestionJobStatus = IngestionJobStatus.STARTED,
                   embedding_model: Optional[str] = None, pipeline_version: Optional[str] = None,
                   ingestion_type: Optional[str] = None) -> IngestionJobEntity:
        """Create an ingestion job. Accepts IngestionJobStatus enum and persists its string value."""
        job_id = self._repo.create_job(content_source_id=content_source_id, status=status.value,
                                       embedding_model=embedding_model, pipeline_version=pipeline_version,
                                       ingestion_type=ingestion_type)
        model = self._repo.get_by_id(job_id)
        entity = IngestionJobMapper.model_to_entity(model)
        assert entity is not None
        return entity

    def update_job(self, job_id: UUID, status: IngestionJobStatus, error_message: Optional[str] = None) -> None:
        """Update a job — accept IngestionJobStatus enum and persist its string value."""
        self._repo.update_job(job_id=job_id, status=status.value, error_message=error_message)

    def get_by_id(self, job_id: UUID) -> Optional[IngestionJobEntity]:
        model = self._repo.get_by_id(job_id)
        return IngestionJobMapper.model_to_entity(model)

    def list_by_content_source(self, content_source_id: UUID) -> List[IngestionJobEntity]:
        models = self._repo.list_by_content_source(content_source_id)
        return IngestionJobMapper.model_list_to_entities(models)

    def list_recent_jobs(self, limit: int = 50) -> List[IngestionJobEntity]:
        """List recent ingestion jobs, ordered by creation date."""
        models = self._repo.list_recent_jobs(limit=limit)
        return IngestionJobMapper.model_list_to_entities(models)

    def list_recent_jobs_by_subject(self, subject_id: UUID, limit: int = 50) -> List[IngestionJobEntity]:
        """List recent ingestion jobs for a specific subject."""
        models = self._repo.list_recent_jobs_by_subject(subject_id, limit=limit)
        return IngestionJobMapper.model_list_to_entities(models)

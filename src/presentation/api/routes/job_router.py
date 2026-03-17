from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException

from src.config.logger import Logger
from src.infrastructure.services.ingestion_job_service import IngestionJobService
from src.presentation.api.dependencies import get_job_service
from src.presentation.api.schemas.job_schemas import JobResponse

logger = Logger()
router = APIRouter()


@router.get(
    "",
    response_model=List[JobResponse],
    responses={500: {"description": "Internal server error"}},
)
def get_jobs(job_service: Annotated[IngestionJobService, Depends(get_job_service)]):
    """Retrieve all ingestion jobs"""
    try:
        jobs = job_service.list_recent_jobs()
        return jobs
    except Exception as e:
        logger.error(f"Error fetching jobs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

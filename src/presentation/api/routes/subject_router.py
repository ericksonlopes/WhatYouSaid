from typing import Annotated, List

from fastapi import APIRouter, Body, Depends, HTTPException

from src.config.logger import Logger
from src.infrastructure.services.knowledge_subject_service import (
    KnowledgeSubjectService,
)
from src.presentation.api.dependencies import get_ks_service
from src.presentation.api.schemas.subject_schemas import SubjectCreate, SubjectResponse

logger = Logger()
router = APIRouter()


@router.post(
    "",
    response_model=SubjectResponse,
    status_code=201,
    responses={500: {"description": "Internal server error"}},
)
def create_subject(
    subject: Annotated[SubjectCreate, Body()],
    ks_service: Annotated[KnowledgeSubjectService, Depends(get_ks_service)],
):
    """Create a new knowledge subject"""
    try:
        created = ks_service.create_subject(
            name=subject.name,
            description=subject.description,
            icon=subject.icon,
            external_ref=subject.external_ref,
        )
        return created
    except Exception as e:
        logger.error(f"Error creating subject: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "",
    response_model=List[SubjectResponse],
    responses={500: {"description": "Internal server error"}},
)
def get_subjects(
    ks_service: Annotated[KnowledgeSubjectService, Depends(get_ks_service)],
):
    """Retrieve all knowledge subjects"""
    try:
        subjects = ks_service.list_subjects()
        return subjects
    except Exception as e:
        logger.error(f"Error fetching subjects: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

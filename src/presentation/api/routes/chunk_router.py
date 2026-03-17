from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from src.config.logger import Logger
from src.infrastructure.services.chunk_index_service import ChunkIndexService
from src.presentation.api.dependencies import get_chunk_index_service
from src.presentation.api.schemas.chunk_schemas import ChunkResponse

logger = Logger()
router = APIRouter()


@router.get(
    "",
    response_model=List[ChunkResponse],
    responses={500: {"description": "Internal server error"}},
)
def get_chunks(
    chunk_service: Annotated[ChunkIndexService, Depends(get_chunk_index_service)],
    source_id: Annotated[Optional[UUID], Query()] = None,
    q: Annotated[Optional[str], Query()] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    """Retrieve text chunks with optional filtering by source or search query"""
    try:
        chunks = chunk_service.list_chunks(
            limit=limit, offset=offset, source_id=source_id, search_query=q
        )
        return chunks
    except Exception as e:
        logger.error(f"Error fetching chunks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

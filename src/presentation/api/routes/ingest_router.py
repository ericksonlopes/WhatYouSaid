from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException

from src.application.dtos.commands.ingest_youtube_command import IngestYoutubeCommand
from src.application.use_cases.ingest_youtube_use_case import IngestYoutubeUseCase
from src.config.logger import Logger
from src.presentation.api.dependencies import get_ingest_youtube_use_case
from src.presentation.api.schemas.ingest_schemas import (
    IngestResponse,
    YoutubeIngestRequest,
)

logger = Logger()
router = APIRouter()


@router.post(
    "/youtube",
    response_model=IngestResponse,
    responses={
        400: {"description": "Validation error or invalid request"},
        500: {"description": "Internal server error during ingestion"},
    },
)
def ingest_youtube(
    request: Annotated[YoutubeIngestRequest, Body()],
    use_case: Annotated[IngestYoutubeUseCase, Depends(get_ingest_youtube_use_case)],
):
    """
    Ingest data from YouTube videos or playlists into the vector store.
    """
    logger.info(
        "API request to ingest youtube",
        context={"video_url": request.video_url, "video_urls": request.video_urls},
    )

    cmd = IngestYoutubeCommand(
        video_url=request.video_url,
        video_urls=request.video_urls,
        subject_id=request.subject_id,
        subject_name=request.subject_name,
        title=request.title,
        language=request.language,
        tokens_per_chunk=request.tokens_per_chunk,
        tokens_overlap=request.tokens_overlap,
        data_type=request.data_type,
        ingestion_job_id=request.ingestion_job_id,
    )

    try:
        result = use_case.execute(cmd)

        # Check if the ingestion was skipped because the source already exists
        if result.skipped:
            raise HTTPException(
                status_code=409,
                detail=result.reason or "This content has already been ingested.",
            )

        return result
    except HTTPException:
        raise
    except ValueError as ve:
        logger.warning(f"Validation error in youtube ingestion: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error executing youtube ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

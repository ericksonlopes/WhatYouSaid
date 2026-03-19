from typing import Annotated, Dict, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, BackgroundTasks

from src.application.dtos.commands.ingest_youtube_command import IngestYoutubeCommand
from src.application.dtos.commands.ingest_file_command import IngestFileCommand
from src.application.use_cases.youtube_ingestion_use_case import YoutubeIngestionUseCase
from src.application.use_cases.file_ingestion_use_case import FileIngestionUseCase
from src.config.logger import Logger
from src.presentation.api.dependencies import (
    get_ingest_youtube_use_case,
    get_file_ingestion_use_case,
)
from src.presentation.api.schemas.ingest_schemas import (
    IngestResponse,
    YoutubeIngestRequest,
)

import os
import shutil
import tempfile
from uuid import UUID
from fastapi import UploadFile, File, Form

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
    use_case: Annotated[YoutubeIngestionUseCase, Depends(get_ingest_youtube_use_case)],
    background_tasks: BackgroundTasks,
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
        reprocess=request.reprocess,
    )

    # If it's a reprocess request, we always run it in background
    if request.reprocess:
        logger.info("Running reprocessing in background")
        background_tasks.add_task(use_case.execute, cmd)
        return IngestResponse(
            skipped=False, reason="Reprocessing started in background."
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


@router.post(
    "/file",
    response_model=Dict,
    responses={
        400: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
async def ingest_file(
    background_tasks: BackgroundTasks,
    use_case: Annotated[FileIngestionUseCase, Depends(get_file_ingestion_use_case)],
    file: Annotated[UploadFile, File(...)],
    subject_id: Annotated[Optional[str], Form()] = None,
    subject_name: Annotated[Optional[str], Form()] = None,
    title: Annotated[Optional[str], Form()] = None,
    language: Annotated[str, Form()] = "pt",
    tokens_per_chunk: Annotated[int, Form()] = 512,
    tokens_overlap: Annotated[int, Form()] = 50,
):
    """
    Upload and ingest a file using Docling.
    """
    logger.info(
        "API request to ingest file",
        context={"file_name": file.filename, "subject_id": subject_id},
    )

    # Validate IDs
    s_id = None
    if subject_id:
        try:
            s_id = UUID(subject_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid subject_id format")

    # Validate filename
    filename = file.filename
    if not filename:
        raise HTTPException(status_code=400, detail="File name is missing")

    # Save uploaded file to a temporary location
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, filename)

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    cmd = IngestFileCommand(
        file_path=temp_path,
        file_name=filename,
        subject_id=s_id,
        subject_name=subject_name,
        title=title,
        language=language,
        tokens_per_chunk=tokens_per_chunk,
        tokens_overlap=tokens_overlap,
    )

    # Execute ingestion in background to avoid timeout
    # Note: The temp file should be deleted AFTER ingestion
    def run_ingestion_and_cleanup(command: IngestFileCommand):
        try:
            use_case.execute(command)
        finally:
            if os.path.exists(command.file_path):
                os.remove(command.file_path)
                os.rmdir(os.path.dirname(command.file_path))

    background_tasks.add_task(run_ingestion_and_cleanup, cmd)

    return {
        "message": "File upload successful, ingestion started in background.",
        "file_name": file.filename,
    }

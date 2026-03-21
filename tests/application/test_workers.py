from unittest.mock import MagicMock, patch
import pytest
from src.application.service_registry import registry
from src.application.workers import run_file_ingestion_worker, run_youtube_ingestion_worker
from src.application.dtos.commands.ingest_file_command import IngestFileCommand
from src.application.dtos.commands.ingest_youtube_command import IngestYoutubeCommand
from src.application.dtos.enums.youtube_data_type import YoutubeDataType

class TestWorkers:
    @pytest.fixture(autouse=True)
    def setup_registry(self):
        # Clear and setup registry
        registry._services = {}
        mock_app = MagicMock()
        registry.register("app", mock_app)
        yield
        registry._services = {}

    def test_run_file_ingestion_worker_success(self):
        # Patch the dependencies module that is imported inside run_file_ingestion_worker
        with patch("src.presentation.api.dependencies.get_settings"), \
             patch("src.presentation.api.dependencies.get_ks_service"), \
             patch("src.presentation.api.dependencies.get_subject_repo"), \
             patch("src.presentation.api.dependencies.get_source_repo"), \
             patch("src.presentation.api.dependencies.get_job_repo"), \
             patch("src.presentation.api.dependencies.get_chunk_repo"), \
             patch("src.presentation.api.dependencies.get_cs_service"), \
             patch("src.presentation.api.dependencies.get_job_service"), \
             patch("src.presentation.api.dependencies.get_model_loader"), \
             patch("src.presentation.api.dependencies.get_embedding_service"), \
             patch("src.presentation.api.dependencies.get_chunk_index_service"), \
             patch("src.presentation.api.dependencies.get_vector_repository"), \
             patch("src.presentation.api.dependencies.get_rerank_service"), \
             patch("src.presentation.api.dependencies.get_chunk_vector_service"), \
             patch("src.presentation.api.dependencies.get_event_bus"), \
             patch("src.application.use_cases.file_ingestion_use_case.FileIngestionUseCase") as mock_use_case_cls:
            
            mock_use_case = MagicMock()
            mock_use_case_cls.return_value = mock_use_case
            
            cmd = IngestFileCommand(file_path="test.pdf", file_name="test.pdf", subject_name="test")
            run_file_ingestion_worker(cmd)
            mock_use_case.execute.assert_called_once_with(cmd)

    def test_run_file_ingestion_worker_no_app(self):
        registry._services = {} # Remove app
        cmd = IngestFileCommand(file_path="test.pdf", file_name="test.pdf", subject_name="test")
        with patch("src.application.workers.logger") as mock_logger:
            run_file_ingestion_worker(cmd)
            mock_logger.error.assert_called_once()

    def test_run_youtube_ingestion_worker_success(self):
        with patch("src.presentation.api.dependencies.get_settings"), \
             patch("src.presentation.api.dependencies.get_ks_service"), \
             patch("src.presentation.api.dependencies.get_subject_repo"), \
             patch("src.presentation.api.dependencies.get_source_repo"), \
             patch("src.presentation.api.dependencies.get_job_repo"), \
             patch("src.presentation.api.dependencies.get_chunk_repo"), \
             patch("src.presentation.api.dependencies.get_cs_service"), \
             patch("src.presentation.api.dependencies.get_job_service"), \
             patch("src.presentation.api.dependencies.get_model_loader"), \
             patch("src.presentation.api.dependencies.get_embedding_service"), \
             patch("src.presentation.api.dependencies.get_chunk_index_service"), \
             patch("src.presentation.api.dependencies.get_vector_repository"), \
             patch("src.presentation.api.dependencies.get_youtube_vector_service"), \
             patch("src.presentation.api.dependencies.get_event_bus"), \
             patch("src.application.use_cases.youtube_ingestion_use_case.YoutubeIngestionUseCase") as mock_use_case_cls:

            mock_use_case = MagicMock()
            mock_use_case_cls.return_value = mock_use_case
            
            cmd = IngestYoutubeCommand(
                video_url="https://youtube.com/watch?v=123", 
                subject_name="test",
                data_type=YoutubeDataType.VIDEO
            )
            run_youtube_ingestion_worker(cmd)
            mock_use_case.execute.assert_called_once_with(cmd)

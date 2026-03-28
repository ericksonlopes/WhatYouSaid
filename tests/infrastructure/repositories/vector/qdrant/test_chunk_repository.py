import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone

from src.infrastructure.repositories.vector.qdrant.chunk_repository import (
    ChunkQdrantRepository,
)
from src.infrastructure.repositories.vector.models.chunk_model import ChunkModel
from src.domain.entities.enums.search_mode_enum import SearchMode


class TestChunkQdrantRepository(unittest.TestCase):
    def setUp(self):
        self.mock_connector = MagicMock()
        self.mock_embedding_service = MagicMock()
        self.mock_embedding_service.get_vector_size.return_value = 1536
        self.mock_embedding_service.embed_query.return_value = [0.1] * 1536

        self.collection_name = "test_collection"

        # Patch ensure_collection_exists to avoid connection during init
        with patch.object(ChunkQdrantRepository, "_ensure_collection_exists"):
            self.repo = ChunkQdrantRepository(
                connector=self.mock_connector,
                embedding_service=self.mock_embedding_service,
                collection_name=self.collection_name,
            )

    def test_create_documents(self):
        # Arrange
        doc = ChunkModel(
            id=uuid4(),
            job_id=uuid4(),
            content_source_id=uuid4(),
            source_type="YOUTUBE",
            content="test content",
            created_at=datetime.now(timezone.utc),
        )

        mock_client = MagicMock()
        self.mock_connector.__enter__.return_value = mock_client

        # Act
        ids = self.repo.create_documents([doc])

        # Assert
        self.assertEqual(ids, [str(doc.id)])
        mock_client.upsert.assert_called_once()
        self.mock_embedding_service.embed_query.assert_called_with("test content")

    def test_semantic_search(self):
        # Arrange
        mock_client = MagicMock()
        self.mock_connector.__enter__.return_value = mock_client

        mock_hit = MagicMock()
        mock_hit.id = str(uuid4())
        mock_hit.score = 0.9
        mock_hit.payload = {
            "id": str(uuid4()),
            "job_id": str(uuid4()),
            "content_source_id": str(uuid4()),
            "source_type": "YOUTUBE",
            "content": "found content",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        mock_response = MagicMock()
        mock_response.points = [mock_hit]
        mock_client.query_points.return_value = mock_response

        # Act
        results = self.repo.retriever("query", search_mode=SearchMode.SEMANTIC)

        # Assert
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].content, "found content")
        self.assertEqual(results[0].score, 0.9)


if __name__ == "__main__":
    unittest.main()

from typing import List, Optional

from langchain_core.documents import Document
from src.config.logger import Logger
from src.infrastructure.repository.weaviate.youtube_repository import WeaviateYoutubeRepository
from weaviate.collections.classes.filters import _Filters as Filters, Filter

logger = Logger()


class YouTubeWeaviateService:
    def __init__(self, repository: WeaviateYoutubeRepository):
        self._repository = repository

    def index_documents(self, documents: List[Document]) -> List[str]:
        if not documents:
            raise ValueError("No documents provided for indexing")

        result = self._repository.create_documents(documents)

        return result

    def search(self, query: str, filters: Optional[Filters] = None, top_k: int = 5) -> List[Document]:
        results = self._repository.retriever(query=query, filters=filters, top_kn=top_k)

        return results if results is not None else []

    def search_by_video_id(self, video_id: str, filters: Optional[Filters] = None) -> List[Document]:
        if not video_id:
            raise ValueError("video_id must be provided")

        combined_filters: Filters = Filter.all_of([
            filters if filters is not None else None
        ])

        results = self._repository.retriever(query="", filters=combined_filters, top_kn=5)

        return results if results is not None else []

    def delete_by_video_id(self, video_id: str) -> int:
        if not video_id:
            raise ValueError("video_id must be provided")

        filters: Filters = Filter.all_of([
            Filter.by_property("video_id").equal(video_id)
        ])

        result = self._repository.delete(video_id, filters=filters)

        return result

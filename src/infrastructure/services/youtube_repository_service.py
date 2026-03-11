from typing import List, Optional, Any

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

        logger.info("Indexing documents via YouTubeWeaviateService", context={"num_documents": len(documents)})

        result = self._repository.create_documents(documents)

        return result

    def search(self, query: str, filters: Optional[Filters] = None, top_k: int = 5) -> List[Document]:
        logger.info("Search called on YouTubeWeaviateService", context={"query": query, "top_k": top_k})

        results = self._repository.retriever(query=query, filters=filters, top_kn=top_k)

        return results if results is not None else []

    def search_by_video_id(self, video_id: str, filters: Optional[Filters] = None) -> List[Document]:
        if not video_id:
            raise ValueError("video_id must be provided")

        logger.info("Search by video_id called on YouTubeWeaviateService", context={"video_id": video_id})

        combined_filters: Filters = Filter.all_of([
            Filter.by_property("video_id").equal(video_id),
            filters if filters is not None else None
        ])

        results = self._repository.retriever(query="", filters=combined_filters, top_kn=5)

        return results if results is not None else []

    def get_retriever(self, filters: Optional[Filters] = None, top_k: int = 5) -> Any:
        """Retorna um retriever configurado (pass-through para testes/integrations)."""
        vector_store = getattr(self._repository, "vector_store", None)
        if vector_store is None:
            raise RuntimeError("Underlying repository does not expose a vector_store")

        with vector_store as vs:
            retriever = vs.as_retriever(search_kwargs={"k": top_k, "filters": filters})
            return retriever

    def delete_by_video_id(self, video_id: str) -> int:
        if not video_id:
            raise ValueError("video_id must be provided")

        logger.info("Deleting documents by video_id via YouTubeWeaviateService", context={"video_id": video_id})

        filters: Filters = Filter.all_of([
            Filter.by_property("video_id").equal(video_id)
        ])

        result = self._repository.delete(video_id, filters=filters)

        return result

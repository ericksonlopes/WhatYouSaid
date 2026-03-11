from typing import List

from langchain_core.documents import Document
from src.config.logger import Logger
from src.domain.infraestructure.repository.retriver_repository import IRetrieverRepository
from src.infrastructure.repository.weaviate.weaviate_client import WeaviateClient
from src.infrastructure.repository.weaviate.weaviate_vector import WeaviateVector
from src.infrastructure.services.embeddding_service import EmbeddingService
from weaviate.collections.classes.filters import _Filters as Filters

logger = Logger()


class WeaviateYoutubeRepository(IRetrieverRepository):
    def __init__(self, weaviate_client: WeaviateClient, embedding_service: EmbeddingService, collection_name: str):
        self._weaviate_client: WeaviateClient = weaviate_client
        self._collection_name = collection_name
        self._embedding_service = embedding_service

        self.vector_store: WeaviateVector = WeaviateVector(
            client=weaviate_client,
            embedding_service=self._embedding_service,
            index_name=collection_name,
            text_key="content"
        )

    def create_documents(self, documents: List[Document]) -> List[str]:
        logger.info("Creating documents in Weaviate", context={"num_documents": len(documents)})

        try:
            texts = [doc.page_content for doc in documents]
            metadatas = [doc.metadata for doc in documents]

            with self.vector_store as vector_store:
                created_ids = vector_store.add_texts(texts=texts, metadatas=metadatas)

            logger.info("Created documents in Weaviate", context={"num_documents": len(documents),
                                                                  "created_ids_count": len(
                                                                      created_ids) if created_ids is not None else 0})
            return created_ids if created_ids is not None else []

        except Exception as e:
            logger.error("Error creating documents in Weaviate",
                         context={"num_documents": len(documents), "error": str(e)})
            return e

    def retriever(self, query: str, filters: Filters, top_kn=5) -> List[Document]:
        logger.info("Retrieving", context={
            "filters": filters,
            "query": query,
            "top_kn": top_kn
        })

        with self.vector_store as vector_store:
            retriever = vector_store.as_retriever(
                search_kwargs={
                    "k": top_kn,
                    "filters": filters
                }
            )
            results = retriever.invoke(query)
            logger.info("Retrieved documents", context={"query": query, "results": len(results)})
            return results

    def delete(self, video_id: str, filters: Filters) -> int:
        logger.info("Deleting documents", context={"video_id": video_id, "filters": filters})
        try:
            with self._weaviate_client as client:
                collection = client.collections.get(self._collection_name)
                result = collection.data.delete_many(where=filters)

                deleted = result.matches if result is not None else 0

                logger.info("Deleted documents", context={"video_id": video_id, "filters": filters, "deleted": deleted})
                return deleted
        except Exception as e:
            logger.error("Error deleting documents",
                         context={"video_id": video_id, "filters": filters, "error": str(e)})
            return e

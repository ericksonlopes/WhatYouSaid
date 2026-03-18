import uuid

from src.config.settings import VectorConfig
from src.domain.entities.enums.search_mode_enum import SearchMode
from src.infrastructure.repositories.vector.models.chunk_model import ChunkModel
from src.infrastructure.repositories.vector.weaviate.chunk_repository import (
    ChunkWeaviateRepository,
)
from src.infrastructure.repositories.vector.weaviate.weaviate_client import (
    WeaviateClient,
)
from src.infrastructure.services.embedding_service import EmbeddingService
from src.infrastructure.services.model_loader_service import ModelLoaderService


def test_search_engines_weaviate():
    print("🔍 Starting Search Quality Test (Weaviate)...")

    # Configuration to connect to local container
    cfg = VectorConfig(
        weaviate_host="localhost",
        weaviate_port=8081,
        weaviate_grpc_port=50051,
        collection_name_chunks="TestChunks",
    )

    # Initialize real services
    model_name = "BAAI/bge-m3"
    model_loader = ModelLoaderService(model_name=model_name)
    embedding_service = EmbeddingService(model_loader_service=model_loader)

    weaviate_client = WeaviateClient(vector_config=cfg)

    # Ensure the collection exists with the correct schema
    weaviate_client.create_collection_if_not_exists(cfg.collection_name_chunks)

    repo = ChunkWeaviateRepository(
        weaviate_client=weaviate_client,
        embedding_service=embedding_service,
        collection_name=cfg.collection_name_chunks,
    )

    # Instead of total deletion, we just create new documents
    # to ensure the search works.
    print("🧹 (Note: Total deletion skipped to avoid filter issues in v4)")

    # Unique IDs for this test to avoid collisions
    job_id = uuid.uuid4()
    source_id = uuid.uuid4()
    subject_id = uuid.uuid4()

    # 1. Preparing test data
    documents = [
        ChunkModel(
            id=uuid.uuid4(),
            job_id=job_id,
            content_source_id=source_id,
            subject_id=subject_id,
            embedding_model=model_name,
            content="Marine biology studies life in the oceans and aquatic ecosystems.",
            external_source="nature_docs",
            source_type="text",
        ),
        ChunkModel(
            id=uuid.uuid4(),
            job_id=job_id,
            content_source_id=source_id,
            subject_id=subject_id,
            embedding_model=model_name,
            content="Quantum physics explores the behavior of matter at the atomic level.",
            external_source="science_journal",
            source_type="text",
        ),
        ChunkModel(
            id=uuid.uuid4(),
            job_id=job_id,
            content_source_id=source_id,
            subject_id=subject_id,
            embedding_model=model_name,
            content="The study of coral reefs is essential for imaginary marine quantum biology.",
            external_source="hybrid_source",
            source_type="text",
        ),
    ]

    print(f"📦 Indexing {len(documents)} documents in Weaviate...")
    repo.create_documents(documents)

    # --- TEST 1: SEMANTIC ---
    print("\n--- Test 1: Semantic Search ---")
    query_semantic = "sea animals"
    results = repo.retriever(query_semantic, top_kn=2, search_mode=SearchMode.SEMANTIC)
    print(f"Query: '{query_semantic}'")
    for i, r in enumerate(results):
        print(f"  [{i + 1}] Score: {r.score:.4f} | Content: {r.content[:50]}...")

    # --- TEST 2: BM25 (KEYWORD) ---
    print("\n--- Test 2: BM25 Search (Keyword) ---")
    query_keyword = "quantum"
    results = repo.retriever(query_keyword, top_kn=1, search_mode=SearchMode.BM25)
    print(f"Query: '{query_keyword}'")
    if results:
        print(f"  [OK] Found: {results[0].content[:50]}...")
    else:
        print("  [ERROR] Nothing found for 'quantum'")

    # --- TEST 3: HYBRID ---
    print("\n--- Test 3: Hybrid Search (Native Weaviate) ---")
    query_hybrid = "atomic ocean"
    results = repo.retriever(query_hybrid, top_kn=2, search_mode=SearchMode.HYBRID)
    print(f"Query: '{query_hybrid}'")
    for i, r in enumerate(results):
        print(f"  [{i + 1}] Score: {r.score:.4f} | Content: {r.content[:50]}...")

    print("\n✅ Test completed successfully!")


if __name__ == "__main__":
    test_search_engines_weaviate()

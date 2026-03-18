import os
import shutil
import uuid

from src.domain.entities.enums.search_mode_enum import SearchMode
from src.infrastructure.repositories.vector.faiss.chunk_repository import (
    ChunkFAISSRepository,
)
from src.infrastructure.repositories.vector.models.chunk_model import ChunkModel
from src.infrastructure.services.embedding_service import EmbeddingService
from src.infrastructure.services.model_loader_service import ModelLoaderService


def test_search_engines():
    print("🔍 Starting Search Quality Test (FAISS)...")

    # Setup
    test_index_path = "./test_vector_index"
    if os.path.exists(test_index_path):
        shutil.rmtree(test_index_path)

    # Initialize real services
    model_name = "BAAI/bge-m3"
    model_loader = ModelLoaderService(model_name=model_name)
    embedding_service = EmbeddingService(model_loader_service=model_loader)

    repo = ChunkFAISSRepository(
        embedding_service=embedding_service,
        index_path=test_index_path,
        index_name="test_chunks",
    )

    # Common IDs for testing
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
            content="Artificial intelligence is revolutionizing software development with LLMs.",
            external_source="tech_news",
            source_type="text",
        ),
        ChunkModel(
            id=uuid.uuid4(),
            job_id=job_id,
            content_source_id=source_id,
            subject_id=subject_id,
            embedding_model=model_name,
            content="The carrot cake recipe with chocolate topping is a Brazilian classic.",
            external_source="culinary_blog",
            source_type="text",
        ),
        ChunkModel(
            id=uuid.uuid4(),
            job_id=job_id,
            content_source_id=source_id,
            subject_id=subject_id,
            embedding_model=model_name,
            content="Apple's new processor uses ARM architecture for maximum energy efficiency.",
            external_source="apple_news",
            source_type="text",
        ),
    ]

    print(f"📦 Indexing {len(documents)} documents...")
    repo.create_documents(documents)

    # --- TEST 1: SEMANTIC ---
    print("\n--- Test 1: Semantic Search ---")
    query_semantic = "computers and technology"
    results = repo.retriever(query_semantic, top_kn=2, search_mode=SearchMode.SEMANTIC)
    print(f"Query: '{query_semantic}'")
    for i, r in enumerate(results):
        print(f"  [{i + 1}] Score: {r.score:.4f} | Content: {r.content[:50]}...")

    # --- TEST 2: BM25 (KEYWORD) ---
    print("\n--- Test 2: BM25 Search (Keyword) ---")
    query_keyword = "carrot"
    results = repo.retriever(query_keyword, top_kn=1, search_mode=SearchMode.BM25)
    print(f"Query: '{query_keyword}'")
    if results:
        print(f"  [OK] Found: {results[0].content[:50]}...")
    else:
        print("  [ERROR] Nothing found for 'carrot'")

    # --- TEST 3: HYBRID (RRF) ---
    print("\n--- Test 3: Hybrid Search (Semantic + Keyword) ---")
    query_hybrid = "processor recipe"
    results = repo.retriever(query_hybrid, top_kn=2, search_mode=SearchMode.HYBRID)
    print(f"Query: '{query_hybrid}'")
    for i, r in enumerate(results):
        print(f"  [{i + 1}] RRF Score: {r.score:.4f} | Content: {r.content[:50]}...")

    # Cleanup
    if os.path.exists(test_index_path):
        shutil.rmtree(test_index_path)
    print("\n✅ Test completed successfully!")


if __name__ == "__main__":
    test_search_engines()

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
    print("🔍 Iniciando Teste de Qualidade de Busca (FAISS)...")

    # Setup
    test_index_path = "./test_vector_index"
    if os.path.exists(test_index_path):
        shutil.rmtree(test_index_path)

    # Inicializa serviços reais
    model_name = "BAAI/bge-m3"
    model_loader = ModelLoaderService(model_name=model_name)
    embedding_service = EmbeddingService(model_loader_service=model_loader)

    repo = ChunkFAISSRepository(
        embedding_service=embedding_service,
        index_path=test_index_path,
        index_name="test_chunks",
    )

    # IDs comuns para o teste
    job_id = uuid.uuid4()
    source_id = uuid.uuid4()
    subject_id = uuid.uuid4()

    # 1. Preparando Massa de Dados
    documents = [
        ChunkModel(
            id=uuid.uuid4(),
            job_id=job_id,
            content_source_id=source_id,
            subject_id=subject_id,
            embedding_model=model_name,
            content="A inteligência artificial está revolucionando o desenvolvimento de software com LLMs.",
            external_source="tech_news",
            source_type="text",
        ),
        ChunkModel(
            id=uuid.uuid4(),
            job_id=job_id,
            content_source_id=source_id,
            subject_id=subject_id,
            embedding_model=model_name,
            content="A receita de bolo de cenoura com cobertura de chocolate é um clássico brasileiro.",
            external_source="culinary_blog",
            source_type="text",
        ),
        ChunkModel(
            id=uuid.uuid4(),
            job_id=job_id,
            content_source_id=source_id,
            subject_id=subject_id,
            embedding_model=model_name,
            content="O novo processador da Apple utiliza arquitetura ARM para máxima eficiência energética.",
            external_source="apple_news",
            source_type="text",
        ),
    ]

    print(f"📦 Indexando {len(documents)} documentos...")
    repo.create_documents(documents)

    # --- TESTE 1: SEMÂNTICO ---
    print("\n--- Teste 1: Busca Semântica ---")
    query_semantic = "computadores e tecnologia"
    results = repo.retriever(query_semantic, top_kn=2, search_mode=SearchMode.SEMANTIC)
    print(f"Query: '{query_semantic}'")
    for i, r in enumerate(results):
        print(f"  [{i + 1}] Score: {r.score:.4f} | Conteúdo: {r.content[:50]}...")

    # --- TESTE 2: BM25 (PALAVRA-CHAVE) ---
    print("\n--- Teste 2: Busca BM25 (Keyword) ---")
    query_keyword = "cenoura"
    results = repo.retriever(query_keyword, top_kn=1, search_mode=SearchMode.BM25)
    print(f"Query: '{query_keyword}'")
    if results:
        print(f"  [OK] Encontrou: {results[0].content[:50]}...")
    else:
        print("  [ERRO] Nada encontrado para 'cenoura'")

    # --- TESTE 3: HÍBRIDO (RRF) ---
    print("\n--- Teste 3: Busca Híbrida (Semântica + Palavra-chave) ---")
    query_hybrid = "receita de processador"
    results = repo.retriever(query_hybrid, top_kn=2, search_mode=SearchMode.HYBRID)
    print(f"Query: '{query_hybrid}'")
    for i, r in enumerate(results):
        print(f"  [{i + 1}] RRF Score: {r.score:.4f} | Conteúdo: {r.content[:50]}...")

    # Cleanup
    if os.path.exists(test_index_path):
        shutil.rmtree(test_index_path)
    print("\n✅ Teste finalizado com sucesso!")


if __name__ == "__main__":
    test_search_engines()

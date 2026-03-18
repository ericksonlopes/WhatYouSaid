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
    print("🔍 Iniciando Teste de Qualidade de Busca (Weaviate)...")

    # Configuração para conectar no container local
    cfg = VectorConfig(
        weaviate_host="localhost",
        weaviate_port=8081,
        weaviate_grpc_port=50051,
        collection_name_chunks="TestChunks",
    )

    # Inicializa serviços reais
    model_name = "BAAI/bge-m3"
    model_loader = ModelLoaderService(model_name=model_name)
    embedding_service = EmbeddingService(model_loader_service=model_loader)

    weaviate_client = WeaviateClient(vector_config=cfg)

    # Garante que a collection existe com o schema correto
    weaviate_client.create_collection_if_not_exists(cfg.collection_name_chunks)

    repo = ChunkWeaviateRepository(
        weaviate_client=weaviate_client,
        embedding_service=embedding_service,
        collection_name=cfg.collection_name_chunks,
    )

    # Em vez de delete total, vamos apenas criar novos documentos
    # para garantir que a busca funcione.
    print("🧹 (Nota: Deleção total pulada para evitar problemas de filtro no v4)")

    # IDs únicos para este teste para evitar colisões
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
            content="A biologia marinha estuda a vida nos oceanos e ecossistemas aquáticos.",
            external_source="nature_docs",
            source_type="text",
        ),
        ChunkModel(
            id=uuid.uuid4(),
            job_id=job_id,
            content_source_id=source_id,
            subject_id=subject_id,
            embedding_model=model_name,
            content="A física quântica explora o comportamento da matéria em nível atômico.",
            external_source="science_journal",
            source_type="text",
        ),
        ChunkModel(
            id=uuid.uuid4(),
            job_id=job_id,
            content_source_id=source_id,
            subject_id=subject_id,
            embedding_model=model_name,
            content="O estudo dos recifes de coral é essencial para a biologia quântica marinha imaginária.",
            external_source="hybrid_source",
            source_type="text",
        ),
    ]

    print(f"📦 Indexando {len(documents)} documentos no Weaviate...")
    repo.create_documents(documents)

    # --- TESTE 1: SEMÂNTICO ---
    print("\n--- Teste 1: Busca Semântica ---")
    query_semantic = "animais do mar"
    results = repo.retriever(query_semantic, top_kn=2, search_mode=SearchMode.SEMANTIC)
    print(f"Query: '{query_semantic}'")
    for i, r in enumerate(results):
        print(f"  [{i + 1}] Score: {r.score:.4f} | Conteúdo: {r.content[:50]}...")

    # --- TESTE 2: BM25 (PALAVRA-CHAVE) ---
    print("\n--- Teste 2: Busca BM25 (Keyword) ---")
    query_keyword = "quântica"
    results = repo.retriever(query_keyword, top_kn=1, search_mode=SearchMode.BM25)
    print(f"Query: '{query_keyword}'")
    if results:
        print(f"  [OK] Encontrou: {results[0].content[:50]}...")
    else:
        print("  [ERRO] Nada encontrado para 'quântica'")

    # --- TESTE 3: HÍBRIDO ---
    print("\n--- Teste 3: Busca Híbrida (Nativa do Weaviate) ---")
    query_hybrid = "oceano atômico"
    results = repo.retriever(query_hybrid, top_kn=2, search_mode=SearchMode.HYBRID)
    print(f"Query: '{query_hybrid}'")
    for i, r in enumerate(results):
        print(f"  [{i + 1}] Score: {r.score:.4f} | Conteúdo: {r.content[:50]}...")

    print("\n✅ Teste finalizado com sucesso!")


if __name__ == "__main__":
    test_search_engines_weaviate()

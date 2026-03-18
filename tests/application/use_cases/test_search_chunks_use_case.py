import uuid
from types import SimpleNamespace

from src.application.use_cases.search_chunks_use_case import SearchChunksUseCase
from src.domain.entities.enums.search_mode_enum import SearchMode


class DummyVectorService:
    def __init__(self):
        self.last_query = None
        self.last_top_k = None
        self.last_filters = None
        self.last_search_mode = None

    def retrieve(
        self, query: str, top_k: int = 5, filters=None, search_mode=SearchMode.SEMANTIC
    ):
        self.last_query = query
        self.last_top_k = top_k
        self.last_filters = filters
        self.last_search_mode = search_mode
        # return dummy chunks as simple objects (avoid ChunkEntity validation in tests)
        return [SimpleNamespace(id=uuid.uuid4(), content="a", subject_id=uuid.uuid4())]


class DummyKS:
    def get_by_name(self, name: str):
        return SimpleNamespace(id=uuid.uuid4(), name=name)


def test_search_filters_by_subject_id():
    vec = DummyVectorService()
    uc = SearchChunksUseCase(vector_service=vec, ks_service=None)

    uc.execute(query="hello", top_k=3, subject_id=uuid.uuid4())

    assert vec.last_query == "hello"
    assert vec.last_top_k == 3
    assert vec.last_filters is not None


def test_search_resolves_subject_name(monkeypatch):
    vec = DummyVectorService()
    ks = DummyKS()
    uc = SearchChunksUseCase(vector_service=vec, ks_service=ks)

    uc.execute(query="hello", top_k=2, subject_name="Alice")

    assert vec.last_query == "hello"
    assert vec.last_top_k == 2
    assert vec.last_filters is not None


def test_search_default_mode_is_semantic():
    vec = DummyVectorService()
    uc = SearchChunksUseCase(vector_service=vec, ks_service=None)

    result = uc.execute(query="hello", top_k=3)

    assert vec.last_search_mode == SearchMode.SEMANTIC
    assert result.search_mode == "semantic"


def test_search_passes_bm25_mode_to_service():
    vec = DummyVectorService()
    uc = SearchChunksUseCase(vector_service=vec, ks_service=None)

    result = uc.execute(query="hello", top_k=3, search_mode=SearchMode.BM25)

    assert vec.last_search_mode == SearchMode.BM25
    assert result.search_mode == "bm25"


def test_search_passes_hybrid_mode_to_service():
    vec = DummyVectorService()
    uc = SearchChunksUseCase(vector_service=vec, ks_service=None)

    result = uc.execute(query="hello", top_k=3, search_mode=SearchMode.HYBRID)

    assert vec.last_search_mode == SearchMode.HYBRID
    assert result.search_mode == "hybrid"

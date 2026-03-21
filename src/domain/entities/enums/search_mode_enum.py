from enum import Enum


class SearchMode(Enum):
    """Enum for available search modes."""

    SEMANTIC = "semantic"
    BM25 = "bm25"
    HYBRID = "hybrid"

from dataclasses import dataclass, field
from typing import List
from src.domain.entities.chunk_entity import ChunkEntity


@dataclass
class SearchChunksResult:
    """Result of a semantic search operation."""

    query: str
    results: List[ChunkEntity] = field(default_factory=list)
    total_count: int = 0

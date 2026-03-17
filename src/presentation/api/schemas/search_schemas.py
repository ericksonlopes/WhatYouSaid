from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class SearchRequest(BaseModel):
    query: str = Field(
        ...,
        description="A query string to search for",
        json_schema_extra={"examples": ["Quem é o palestrante?"]},
    )
    top_k: int = Field(default=5, ge=1, le=50)
    subject_id: Optional[str] = None
    subject_name: Optional[str] = None


class ChunkResultSchema(BaseModel):
    id: UUID
    content_source_id: Optional[UUID] = None
    content: Optional[str] = None
    external_source: Optional[str] = None
    source_type: Optional[str] = None
    tokens_count: Optional[int] = None
    language: Optional[str] = None
    embedding_model: Optional[str] = None
    created_at: Optional[datetime] = None
    score: Optional[float] = None
    extra: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)


class SearchResponse(BaseModel):
    query: str
    results: List[ChunkResultSchema]
    total_count: int

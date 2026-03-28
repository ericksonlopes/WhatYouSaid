from typing import Optional

from pydantic import BaseModel


class AppSettingsSchema(BaseModel):
    env: str
    log_levels: str


class VectorSettingsSchema(BaseModel):
    store_type: str
    weaviate_host: Optional[str] = None
    weaviate_port: Optional[int] = None
    weaviate_grpc_port: Optional[int] = None
    weaviate_collection: Optional[str] = None
    qdrant_host: Optional[str] = None
    qdrant_port: Optional[int] = None
    qdrant_grpc_port: Optional[int] = None
    qdrant_collection: Optional[str] = None


class ModelSettingsSchema(BaseModel):
    name: str


class SQLSettingsSchema(BaseModel):
    type: Optional[str] = None
    database: Optional[str] = None


class RedisSettingsSchema(BaseModel):
    host: str
    port: int
    db: int


class SettingsResponse(BaseModel):
    app: AppSettingsSchema
    vector: VectorSettingsSchema
    model: ModelSettingsSchema
    sql: SQLSettingsSchema
    redis: RedisSettingsSchema


class HealthCheckResponse(BaseModel):
    status: str
    latency_ms: Optional[int] = None
    message: Optional[str] = None

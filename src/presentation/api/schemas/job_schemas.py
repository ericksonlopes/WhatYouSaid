from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class JobResponse(BaseModel):
    id: UUID
    status: str
    current_step: Optional[int] = 0
    total_steps: Optional[int] = 0
    status_message: Optional[str] = None
    error_message: Optional[str] = None
    ingestion_type: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

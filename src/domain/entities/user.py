from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    email: str
    full_name: Optional[str] = None
    picture_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "validate_assignment": True,
    }

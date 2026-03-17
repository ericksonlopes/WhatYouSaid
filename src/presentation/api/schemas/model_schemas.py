from pydantic import BaseModel


class ModelInfoResponse(BaseModel):
    name: str
    dimensions: int
    max_seq_length: int

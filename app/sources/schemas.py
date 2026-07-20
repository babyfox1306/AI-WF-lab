from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SourceCreate(BaseModel):
    source_type: str = Field(default="generic_text")
    title: str = Field(..., min_length=1, max_length=255)
    raw_text: str = Field(..., min_length=1)


class SourceResponse(BaseModel):
    id: int
    project_id: Optional[int] = None
    source_type: str
    title: str
    raw_text: str
    checksum: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}

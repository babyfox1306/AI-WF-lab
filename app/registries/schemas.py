from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class RegistryCreate(BaseModel):
    key: str = Field(..., max_length=255)
    value: Any = None
    category: str = Field(default="job_requirement")
    source_document_id: Optional[int] = None
    confidence: float = Field(default=1.0, ge=0, le=1)
    locked: bool = False


class RegistryUpdate(BaseModel):
    locked: Optional[bool] = None
    confidence: Optional[float] = Field(None, ge=0, le=1)
    value: Any = None


class RegistryResponse(BaseModel):
    id: int
    project_id: int
    key: str
    value: Any = None
    category: str
    source_document_id: Optional[int] = None
    confidence: float
    locked: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    workspace_id: int
    name: str = Field(..., min_length=1, max_length=255)
    project_type: str = Field(default="upwork_opportunity")
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = Field(None, pattern=r"^(draft|ready|running|awaiting_approval|completed|failed|archived)$")
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    workspace_id: int
    name: str
    project_type: str
    status: str
    description: Optional[str] = ""
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

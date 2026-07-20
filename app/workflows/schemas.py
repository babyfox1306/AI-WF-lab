from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WorkflowCreate(BaseModel):
    """Schema for creating a workflow."""

    name: str = Field(..., min_length=1, max_length=255, description="Workflow name")
    description: Optional[str] = Field("", description="Workflow description")


class WorkflowUpdate(BaseModel):
    """Schema for updating a workflow."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = Field(
        None, pattern=r"^(draft|running|completed|failed)$"
    )


class WorkflowResponse(BaseModel):
    """Schema for returning workflow data."""

    id: int
    workspace_id: int
    name: str
    description: Optional[str] = ""
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}

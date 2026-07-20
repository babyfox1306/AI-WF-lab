from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WorkspaceCreate(BaseModel):
    """Schema for creating a workspace."""

    name: str = Field(..., min_length=1, max_length=255, description="Workspace name")


class WorkspaceUpdate(BaseModel):
    """Schema for updating a workspace."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)


class WorkspaceResponse(BaseModel):
    """Schema for returning workspace data."""

    id: int
    name: str
    owner_id: int
    created_at: datetime

    model_config = {"from_attributes": True}

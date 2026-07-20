from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ToolCreate(BaseModel):
    workspace_id: int
    name: str = Field(..., max_length=255)
    slug: str = Field(..., max_length=255)
    description: Optional[str] = None
    tool_type: str = Field(default="http")
    endpoint: Optional[str] = None
    http_method: str = "POST"
    request_schema: Optional[str] = None
    response_schema: Optional[str] = None
    headers_config: Optional[str] = None
    timeout_seconds: int = 30


class ToolUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ToolResponse(BaseModel):
    id: int
    workspace_id: int
    name: str
    slug: str
    description: Optional[str] = ""
    tool_type: str
    endpoint: Optional[str] = None
    http_method: str
    timeout_seconds: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AgentCreate(BaseModel):
    workspace_id: int
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    role: str = Field(..., max_length=255)
    system_prompt: str = Field(...)
    provider_connection_id: Optional[int] = None
    model_override: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_output_tokens: int = Field(default=4096, ge=1)
    output_schema: Optional[str] = None


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    role: Optional[str] = None
    system_prompt: Optional[str] = None
    provider_connection_id: Optional[int] = None
    model_override: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0, le=2)
    max_output_tokens: Optional[int] = Field(None, ge=1)
    output_schema: Optional[str] = None
    is_active: Optional[bool] = None


class AgentResponse(BaseModel):
    id: int
    workspace_id: int
    name: str
    slug: str
    description: Optional[str] = ""
    role: str
    system_prompt: str
    provider_connection_id: Optional[int] = None
    model_override: Optional[str] = None
    temperature: float
    max_output_tokens: int
    output_schema: Optional[str] = "{}"
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

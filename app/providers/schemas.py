from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProviderCreate(BaseModel):
    """Schema for creating a provider connection."""

    name: str = Field(..., min_length=1, max_length=255)
    provider_type: str = Field(default="openai_compatible", pattern=r"^(openai_compatible|ollama)$")
    base_url: str = Field(..., max_length=512)
    api_key: Optional[str] = Field(None, max_length=1024)
    default_model: Optional[str] = Field(None, max_length=255)
    timeout_seconds: int = Field(default=120, ge=5, le=600)


class ProviderUpdate(BaseModel):
    """Schema for updating a provider connection."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    base_url: Optional[str] = Field(None, max_length=512)
    api_key: Optional[str] = Field(None, max_length=1024)
    default_model: Optional[str] = Field(None, max_length=255)
    timeout_seconds: Optional[int] = Field(None, ge=5, le=600)
    is_active: Optional[bool] = None


class ProviderResponse(BaseModel):
    """Schema for returning provider data (masked API key)."""

    id: int
    owner_id: int
    name: str
    provider_type: str
    base_url: str
    api_key_masked: Optional[str] = None
    default_model: Optional[str] = None
    timeout_seconds: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProviderTestResult(BaseModel):
    """Schema for provider connection test result."""

    success: bool
    message: str
    models: Optional[list[str]] = None

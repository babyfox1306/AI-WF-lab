from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Schema for user registration."""

    email: str = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=100, description="Username")
    password: str = Field(..., min_length=6, max_length=255, description="Password")


class UserLogin(BaseModel):
    """Schema for user login."""

    email: str = Field(..., description="User email address")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Schema for returning user data in responses."""

    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    username: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[str] = Field(None)

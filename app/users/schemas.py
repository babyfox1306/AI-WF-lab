from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserResponse(BaseModel):
    """Schema for returning user data."""

    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    username: Optional[str] = None
    email: Optional[str] = None

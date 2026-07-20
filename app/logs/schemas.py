from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LogResponse(BaseModel):
    """Schema for returning log data."""

    id: int
    job_id: int
    level: str
    message: str
    timestamp: datetime

    model_config = {"from_attributes": True}

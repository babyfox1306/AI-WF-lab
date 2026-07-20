import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, model_validator


class JobCreate(BaseModel):
    """Schema for creating a job."""

    name: str = Field(..., min_length=1, max_length=255, description="Job name")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data as JSON")


class JobResponse(BaseModel):
    """Schema for returning job data."""

    id: int
    workflow_id: int
    name: str
    input_data: Optional[Any] = None
    output_data: Optional[Any] = None
    status: str
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def parse_json_fields(cls, data: Any) -> Any:
        """Parse JSON string fields from the database into Python objects."""
        if isinstance(data, dict):
            for field_name in ("input_data", "output_data"):
                value = data.get(field_name)
                if isinstance(value, str):
                    try:
                        data[field_name] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        pass
        elif hasattr(data, "input_data") and isinstance(data.input_data, str):
            # Handle ORM model objects
            try:
                data.input_data = json.loads(data.input_data)
            except (json.JSONDecodeError, TypeError):
                pass
            if hasattr(data, "output_data") and isinstance(data.output_data, str):
                try:
                    data.output_data = json.loads(data.output_data)
                except (json.JSONDecodeError, TypeError):
                    pass
        return data


class LogEntry(BaseModel):
    """Schema for a single log entry in the execute response."""

    level: str
    message: str
    timestamp: datetime


class JobExecuteResponse(BaseModel):
    """Schema for job execution response."""

    job: JobResponse
    logs: List[LogEntry]

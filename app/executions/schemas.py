from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ExecutionCreate(BaseModel):
    pipeline_template_id: int
    idempotency_key: Optional[str] = None


class ExecutionResponse(BaseModel):
    id: int
    project_id: int
    pipeline_template_id: int
    template_version: int
    status: str
    idempotency_key: Optional[str] = None
    requested_by: Optional[int] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    error_message: Optional[str] = None
    current_node_key: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class NodeExecutionResponse(BaseModel):
    id: int
    pipeline_execution_id: int
    node_key: str
    node_type: str
    status: str
    attempt: int
    input_snapshot: Optional[Any] = None
    output_snapshot: Optional[Any] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float
    created_at: datetime

    model_config = {"from_attributes": True}

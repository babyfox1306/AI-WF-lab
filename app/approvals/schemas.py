from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ApprovalResolve(BaseModel):
    decision: str = Field(..., pattern=r"^(approved|rejected|changes_requested)$")
    comment: Optional[str] = None


class ApprovalResponse(BaseModel):
    id: int
    execution_id: int
    node_execution_id: Optional[int] = None
    status: str
    prompt: str
    requested_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    decision: Optional[str] = None
    comment: Optional[str] = None

    model_config = {"from_attributes": True}

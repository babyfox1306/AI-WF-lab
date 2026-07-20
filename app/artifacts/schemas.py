from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class ArtifactResponse(BaseModel):
    id: int
    project_id: int
    execution_id: int
    node_execution_id: Optional[int] = None
    artifact_type: str
    name: str
    content_text: Optional[str] = None
    content_json: Optional[Any] = None
    version: int
    checksum: Optional[str] = None
    is_final: bool
    created_at: datetime

    model_config = {"from_attributes": True}

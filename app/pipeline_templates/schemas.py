from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class TemplateResponse(BaseModel):
    id: int
    workspace_id: Optional[int] = None
    name: str
    slug: str
    description: Optional[str] = ""
    version: int
    graph_definition: Any = None
    input_schema: Any = None
    output_schema: Any = None
    is_system: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

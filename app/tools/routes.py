from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.service import get_current_user
from app.database.database import get_db
from app.tools.models import ToolDefinition
from app.tools.schemas import ToolCreate, ToolResponse, ToolUpdate
from app.workspaces.service import get_workspace, list_workspaces

router = APIRouter(prefix="/tools", tags=["tools"])


@router.post("/", response_model=ToolResponse, status_code=status.HTTP_201_CREATED)
def create(data: ToolCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_workspace(db, data.workspace_id, current_user)
    tool = ToolDefinition(
        workspace_id=data.workspace_id, name=data.name, slug=data.slug,
        description=data.description or "", tool_type=data.tool_type,
        endpoint=data.endpoint, http_method=data.http_method or "POST",
        request_schema=data.request_schema or "{}", response_schema=data.response_schema or "{}",
        headers_config=data.headers_config or "{}", timeout_seconds=data.timeout_seconds or 30,
    )
    db.add(tool)
    db.commit()
    db.refresh(tool)
    return tool


@router.get("/", response_model=List[ToolResponse])
def list_all(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ws_ids = [ws.id for ws in list_workspaces(db, current_user)]
    return db.query(ToolDefinition).filter(ToolDefinition.workspace_id.in_(ws_ids)).all()


@router.get("/{tool_id}", response_model=ToolResponse)
def get(tool_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tool = db.query(ToolDefinition).filter(ToolDefinition.id == tool_id).first()
    if not tool:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Tool not found")
    get_workspace(db, tool.workspace_id, current_user)
    return tool


@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(tool_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tool = db.query(ToolDefinition).filter(ToolDefinition.id == tool_id).first()
    if not tool:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Tool not found")
    get_workspace(db, tool.workspace_id, current_user)
    db.delete(tool)
    db.commit()

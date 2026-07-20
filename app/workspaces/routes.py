from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.service import get_current_user
from app.database.database import get_db
from app.workspaces.schemas import WorkspaceCreate, WorkspaceResponse, WorkspaceUpdate
from app.workspaces.service import (
    create_workspace,
    delete_workspace,
    get_workspace,
    list_workspaces,
    update_workspace,
)

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create(data: WorkspaceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new workspace."""
    return create_workspace(db, data, current_user)


@router.get("/", response_model=List[WorkspaceResponse])
def list_all(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List all workspaces for the current user."""
    return list_workspaces(db, current_user)


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get(workspace_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get a workspace by id."""
    return get_workspace(db, workspace_id, current_user)


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
def update(workspace_id: int, data: WorkspaceUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update a workspace."""
    return update_workspace(db, workspace_id, data, current_user)


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(workspace_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete a workspace."""
    delete_workspace(db, workspace_id, current_user)

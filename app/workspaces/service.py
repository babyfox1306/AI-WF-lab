from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.models import User
from app.workspaces.models import Workspace
from app.workspaces.schemas import WorkspaceCreate, WorkspaceUpdate


def _workspace_not_found(workspace_id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Workspace with id {workspace_id} not found",
    )


def _check_owner(workspace: Workspace, user: User) -> None:
    if workspace.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this workspace",
        )


def create_workspace(db: Session, data: WorkspaceCreate, user: User) -> Workspace:
    """Create a new workspace owned by the user."""
    workspace = Workspace(name=data.name, owner_id=user.id)
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace


def list_workspaces(db: Session, user: User) -> List[Workspace]:
    """List all workspaces owned by the user."""
    return db.query(Workspace).filter(Workspace.owner_id == user.id).order_by(Workspace.created_at.desc()).all()


def get_workspace(db: Session, workspace_id: int, user: User) -> Workspace:
    """Get a workspace by id, with ownership check."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise _workspace_not_found(workspace_id)
    _check_owner(workspace, user)
    return workspace


def update_workspace(db: Session, workspace_id: int, data: WorkspaceUpdate, user: User) -> Workspace:
    """Update a workspace name."""
    workspace = get_workspace(db, workspace_id, user)
    if data.name is not None:
        workspace.name = data.name
    db.commit()
    db.refresh(workspace)
    return workspace


def delete_workspace(db: Session, workspace_id: int, user: User) -> None:
    """Delete a workspace."""
    workspace = get_workspace(db, workspace_id, user)
    db.delete(workspace)
    db.commit()

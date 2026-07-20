from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.models import User
from app.workspaces.service import get_workspace
from app.workflows.models import Workflow
from app.workflows.schemas import WorkflowCreate, WorkflowUpdate


def _workflow_not_found(workflow_id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Workflow with id {workflow_id} not found",
    )


def create_workflow(db: Session, data: WorkflowCreate, workspace_id: int, user: User) -> Workflow:
    """Create a new workflow in a workspace."""
    # Verify workspace exists and user has access
    get_workspace(db, workspace_id, user)

    workflow = Workflow(
        workspace_id=workspace_id,
        name=data.name,
        description=data.description or "",
        status="draft",
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return workflow


def list_workflows(db: Session, workspace_id: int, user: User) -> List[Workflow]:
    """List all workflows in a workspace."""
    # Verify workspace exists and user has access
    get_workspace(db, workspace_id, user)

    return (
        db.query(Workflow)
        .filter(Workflow.workspace_id == workspace_id)
        .order_by(Workflow.created_at.desc())
        .all()
    )


def get_workflow(db: Session, workflow_id: int, user: User) -> Workflow:
    """Get a workflow by id, with workspace ownership check."""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise _workflow_not_found(workflow_id)
    # Verify workspace access
    get_workspace(db, workflow.workspace_id, user)
    return workflow


def update_workflow(db: Session, workflow_id: int, data: WorkflowUpdate, user: User) -> Workflow:
    """Update a workflow."""
    workflow = get_workflow(db, workflow_id, user)
    if data.name is not None:
        workflow.name = data.name
    if data.description is not None:
        workflow.description = data.description
    if data.status is not None:
        workflow.status = data.status
    db.commit()
    db.refresh(workflow)
    return workflow


def delete_workflow(db: Session, workflow_id: int, user: User) -> None:
    """Delete a workflow."""
    workflow = get_workflow(db, workflow_id, user)
    db.delete(workflow)
    db.commit()

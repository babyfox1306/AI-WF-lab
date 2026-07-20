from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.service import get_current_user
from app.database.database import get_db
from app.workflows.schemas import WorkflowCreate, WorkflowResponse, WorkflowUpdate
from app.workflows.service import (
    create_workflow,
    delete_workflow,
    get_workflow,
    list_workflows,
    update_workflow,
)

router = APIRouter(prefix="/workspaces/{workspace_id}/workflows", tags=["workflows"])


@router.post("/", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
def create(
    workspace_id: int,
    data: WorkflowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new workflow in a workspace."""
    return create_workflow(db, data, workspace_id, current_user)


@router.get("/", response_model=List[WorkflowResponse])
def list_all(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all workflows in a workspace."""
    return list_workflows(db, workspace_id, current_user)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get(
    workspace_id: int,
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a workflow by id."""
    return get_workflow(db, workflow_id, current_user)


@router.patch("/{workflow_id}", response_model=WorkflowResponse)
def update(
    workspace_id: int,
    workflow_id: int,
    data: WorkflowUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a workflow."""
    return update_workflow(db, workflow_id, data, current_user)


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    workspace_id: int,
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a workflow."""
    delete_workflow(db, workflow_id, current_user)

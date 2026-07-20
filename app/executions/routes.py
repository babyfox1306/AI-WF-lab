from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.service import get_current_user
from app.database.database import get_db
from app.executions.engine import (
    create_execution, transition_execution,
    create_node_execution, transition_node, get_node_executions_for_execution,
)
from app.executions.models import PipelineExecution
from app.executions.schemas import ExecutionCreate, ExecutionResponse, NodeExecutionResponse
from app.projects.models import OpportunityProject
from app.workspaces.service import get_workspace

router = APIRouter(prefix="/projects/{project_id}/executions", tags=["executions"])


@router.post("/", response_model=ExecutionResponse, status_code=status.HTTP_201_CREATED)
def create(project_id: int, data: ExecutionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(OpportunityProject).filter(OpportunityProject.id == project_id).first()
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")
    get_workspace(db, project.workspace_id, current_user)

    from app.pipeline_templates.models import PipelineTemplate
    template = db.query(PipelineTemplate).filter(PipelineTemplate.id == data.pipeline_template_id).first()
    if not template:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Pipeline template not found")

    import json
    execution = create_execution(
        db=db, project_id=project_id,
        pipeline_template_id=template.id,
        template_version=template.version,
        template_snapshot=json.loads(template.graph_definition),
        requested_by=current_user.id,
        idempotency_key=data.idempotency_key,
    )
    return execution


@router.get("/", response_model=List[ExecutionResponse])
def list_all(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(OpportunityProject).filter(OpportunityProject.id == project_id).first()
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")
    get_workspace(db, project.workspace_id, current_user)
    return db.query(PipelineExecution).filter(PipelineExecution.project_id == project_id).order_by(PipelineExecution.created_at.desc()).all()


@router.get("/{execution_id}", response_model=ExecutionResponse)
def get(project_id: int, execution_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    execution = db.query(PipelineExecution).filter(PipelineExecution.id == execution_id).first()
    if not execution:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Execution not found")
    project = db.query(OpportunityProject).filter(OpportunityProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    get_workspace(db, project.workspace_id, current_user)
    return execution


@router.post("/{execution_id}/cancel", response_model=ExecutionResponse)
def cancel(project_id: int, execution_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    execution = db.query(PipelineExecution).filter(PipelineExecution.id == execution_id).first()
    if not execution:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Execution not found")
    project = db.query(OpportunityProject).filter(OpportunityProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    get_workspace(db, project.workspace_id, current_user)
    return transition_execution(db, execution_id, "cancelled")


@router.post("/{execution_id}/rerun", response_model=ExecutionResponse)
def rerun(project_id: int, execution_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    original = db.query(PipelineExecution).filter(PipelineExecution.id == execution_id).first()
    if not original:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Execution not found")
    project = db.query(OpportunityProject).filter(OpportunityProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    get_workspace(db, project.workspace_id, current_user)

    import json
    execution = create_execution(
        db=db, project_id=project_id,
        pipeline_template_id=original.pipeline_template_id,
        template_version=original.template_version,
        template_snapshot=json.loads(original.template_snapshot or "{}"),
        requested_by=current_user.id,
    )
    return execution


@router.get("/{execution_id}/nodes", response_model=List[NodeExecutionResponse])
def list_nodes(project_id: int, execution_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    execution = db.query(PipelineExecution).filter(PipelineExecution.id == execution_id).first()
    if not execution:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Execution not found")
    project = db.query(OpportunityProject).filter(OpportunityProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    get_workspace(db, project.workspace_id, current_user)
    return get_node_executions_for_execution(db, execution_id)

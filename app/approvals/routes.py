from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.approvals.models import ApprovalRequest
from app.approvals.schemas import ApprovalResolve, ApprovalResponse
from app.auth.models import User
from app.auth.service import get_current_user
from app.database.database import get_db
from app.executions.engine import transition_execution
from app.executions.models import PipelineExecution
from app.projects.models import OpportunityProject
from app.workspaces.service import get_workspace

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("/pending", response_model=List[ApprovalResponse])
def list_pending(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(ApprovalRequest).filter(ApprovalRequest.status == "pending").all()


@router.get("/{approval_id}", response_model=ApprovalResponse)
def get(approval_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    approval = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
    if not approval:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Approval not found")
    return approval


@router.post("/{approval_id}/resolve", response_model=ApprovalResponse, status_code=status.HTTP_200_OK)
def resolve(approval_id: int, data: ApprovalResolve, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from datetime import datetime, timezone
    approval = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
    if not approval:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Approval not found")

    if approval.status != "pending":
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail=f"Approval already {approval.status}")

    approval.status = data.decision
    approval.decision = data.decision
    approval.comment = data.comment
    approval.resolved_at = datetime.now(timezone.utc)
    approval.resolved_by = current_user.id
    db.commit()
    db.refresh(approval)

    # Resume execution if approved
    execution = db.query(PipelineExecution).filter(PipelineExecution.id == approval.execution_id).first()
    if execution and data.decision == "approved":
        transition_execution(db, execution.id, "running")

    return approval

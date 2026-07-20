from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.service import get_current_user
from app.database.database import get_db
from app.jobs.schemas import JobCreate, JobResponse, JobExecuteResponse
from app.jobs.service import create_job, execute_job, get_job, list_jobs

router = APIRouter(prefix="/workflows/{workflow_id}/jobs", tags=["jobs"])


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create(
    workflow_id: int,
    data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new job in a workflow."""
    return create_job(db, data, workflow_id, current_user)


@router.get("/", response_model=List[JobResponse])
def list_all(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all jobs in a workflow."""
    return list_jobs(db, workflow_id, current_user)


@router.get("/{job_id}", response_model=JobResponse)
def get(
    workflow_id: int,
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a job by id."""
    return get_job(db, job_id, current_user)


@router.post("/{job_id}/execute", response_model=JobExecuteResponse)
def execute(
    workflow_id: int,
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Execute a job, simulating AI workflow processing."""
    return execute_job(db, job_id, current_user)

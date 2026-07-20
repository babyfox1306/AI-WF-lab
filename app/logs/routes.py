from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.service import get_current_user
from app.database.database import get_db
from app.logs.schemas import LogResponse
from app.logs.service import list_job_logs

router = APIRouter(prefix="/jobs/{job_id}/logs", tags=["logs"])


@router.get("/", response_model=List[LogResponse])
def list_all(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all logs for a job."""
    return list_job_logs(db, job_id, current_user)

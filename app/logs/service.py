from typing import List

from sqlalchemy.orm import Session

from app.auth.models import User
from app.jobs.service import get_job
from app.logs.models import Log


def list_job_logs(db: Session, job_id: int, user: User) -> List[Log]:
    """List all logs for a job, with access control."""
    # Verify job access
    get_job(db, job_id, user)

    return (
        db.query(Log)
        .filter(Log.job_id == job_id)
        .order_by(Log.timestamp.asc())
        .all()
    )

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.models import User
from app.jobs.models import Job
from app.logs.models import Log
from app.workflows.models import Workflow
from app.workspaces.models import Workspace


def get_dashboard_stats(db: Session, user: User) -> dict:
    """Get dashboard statistics for the current user."""
    # Get all workspace IDs for the user
    workspace_ids = select(Workspace.id).where(Workspace.owner_id == user.id)

    # Get all workflow IDs from user's workspaces
    workflow_ids = select(Workflow.id).where(Workflow.workspace_id.in_(workspace_ids))

    # Total workflows
    total_workflows = (
        db.query(func.count(Workflow.id))
        .filter(Workflow.workspace_id.in_(workspace_ids))
        .scalar()
        or 0
    )

    # Running jobs
    running_jobs = (
        db.query(func.count(Job.id))
        .filter(Job.workflow_id.in_(workflow_ids), Job.status == "running")
        .scalar()
        or 0
    )

    # Completed jobs
    completed_jobs = (
        db.query(func.count(Job.id))
        .filter(Job.workflow_id.in_(workflow_ids), Job.status == "completed")
        .scalar()
        or 0
    )

    # Failed jobs
    failed_jobs = (
        db.query(func.count(Job.id))
        .filter(Job.workflow_id.in_(workflow_ids), Job.status == "failed")
        .scalar()
        or 0
    )

    # Recent activity (last 10 logs across user's jobs)
    recent_activity = []
    recent_logs = (
        db.query(Log)
        .join(Job, Log.job_id == Job.id)
        .filter(Job.workflow_id.in_(workflow_ids))
        .order_by(Log.timestamp.desc())
        .limit(10)
        .all()
    )

    for log in recent_logs:
        recent_activity.append({
            "id": log.id,
            "job_id": log.job_id,
            "level": log.level,
            "message": log.message,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
        })

    return {
        "total_workflows": total_workflows,
        "running_jobs": running_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "recent_activity": recent_activity,
    }

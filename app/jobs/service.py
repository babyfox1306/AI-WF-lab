import json
import random
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.models import User
from app.jobs.models import Job
from app.jobs.schemas import JobCreate, JobExecuteResponse, JobResponse, LogEntry
from app.logs.models import Log
from app.workflows.service import get_workflow


def _job_not_found(job_id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Job with id {job_id} not found",
    )


def create_job(db: Session, data: JobCreate, workflow_id: int, user: User) -> Job:
    """Create a new job in a workflow."""
    # Verify workflow exists and user has access
    get_workflow(db, workflow_id, user)

    job = Job(
        workflow_id=workflow_id,
        name=data.name,
        input_data=json.dumps(data.input_data) if data.input_data else "{}",
        status="pending",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def list_jobs(db: Session, workflow_id: int, user: User) -> List[Job]:
    """List all jobs in a workflow."""
    get_workflow(db, workflow_id, user)
    return (
        db.query(Job)
        .filter(Job.workflow_id == workflow_id)
        .order_by(Job.id.desc())
        .all()
    )


def get_job(db: Session, job_id: int, user: User) -> Job:
    """Get a job by id, with workflow access check."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise _job_not_found(job_id)
    # Verify workflow access
    get_workflow(db, job.workflow_id, user)
    return job


def _simulate_ai_processing(input_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
    """Simulate AI workflow processing. Returns (success, output_data, error_message)."""
    # Simulate processing time
    import time
    time.sleep(0.1)

    # 90% chance of success, 10% chance of failure
    if random.random() < 0.9:
        output = {
            "result": "processed_successfully",
            "input_received": input_data,
            "analysis": {
                "sentiment": random.choice(["positive", "neutral", "negative"]),
                "confidence": round(random.uniform(0.7, 0.99), 2),
                "processing_time_ms": random.randint(100, 500),
            },
        }
        return True, output, ""
    else:
        return False, {}, "AI model processing failed: unexpected input format"


def _create_execution_logs(db: Session, job_id: int, status: str, success: bool) -> List[Dict]:
    """Create logs for a job execution."""
    logs_data = []

    log_entries = [
        ("info", f"Job execution started"),
    ]

    if success:
        log_entries.append(("info", "Input data validated successfully"))
        log_entries.append(("info", "AI model inference completed"))
        log_entries.append(("info", "Post-processing pipeline finished"))
        log_entries.append(("info", "Job completed successfully"))
    else:
        log_entries.append(("warning", "Input data validation warning: non-standard format"))
        log_entries.append(("error", "AI model processing error"))
        log_entries.append(("error", "Job execution failed"))

    timestamp = datetime.now(timezone.utc)
    for i, (level, message) in enumerate(log_entries):
        log = Log(
            job_id=job_id,
            level=level,
            message=message,
            timestamp=timestamp,
        )
        db.add(log)
        logs_data.append({
            "level": level,
            "message": message,
            "timestamp": timestamp,
        })

    db.commit()
    return logs_data


def execute_job(db: Session, job_id: int, user: User) -> JobExecuteResponse:
    """Execute a job, simulating AI workflow processing."""
    job = get_job(db, job_id, user)

    if job.status == "running":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Job is already running",
        )
    if job.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Job is already completed",
        )

    # Mark as running
    job.status = "running"
    job.started_at = datetime.now(timezone.utc)
    db.commit()

    # Simulate AI processing
    input_data = json.loads(job.input_data) if job.input_data else {}
    success, output_data, error_message = _simulate_ai_processing(input_data)

    # Update job result
    job.output_data = json.dumps(output_data) if success else None
    job.status = "completed" if success else "failed"
    job.error_message = error_message if not success else None
    job.finished_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(job)

    # Create execution logs
    logs_data = _create_execution_logs(db, job.id, job.status, success)

    # Update workflow status
    workflow = job.workflow
    workflow.status = "running"
    db.commit()

    # Build response
    # Parse JSON strings back to dicts for response
    job_response = JobResponse(
        id=job.id,
        workflow_id=job.workflow_id,
        name=job.name,
        input_data=json.loads(job.input_data) if job.input_data else {},
        output_data=json.loads(job.output_data) if job.output_data else None,
        status=job.status,
        error_message=job.error_message,
        started_at=job.started_at,
        finished_at=job.finished_at,
    )

    log_entries = [LogEntry(**log) for log in logs_data]

    return JobExecuteResponse(job=job_response, logs=log_entries)

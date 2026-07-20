"""Pipeline execution engine with state machine."""

import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from sqlalchemy.orm import Session

from app.artifacts.models import Artifact
from app.executions.models import PipelineExecution
from app.execution_nodes.models import NodeExecution
from app.pipeline_templates.validator import topological_sort


# Valid state transitions for pipeline execution
EXECUTION_TRANSITIONS: Dict[str, Set[str]] = {
    "queued": {"running", "cancelled"},
    "running": {"awaiting_approval", "completed", "failed", "cancelled"},
    "awaiting_approval": {"running", "cancelled", "failed"},
    "completed": set(),
    "failed": set(),
    "cancelled": set(),
}

# Valid state transitions for node execution
NODE_TRANSITIONS: Dict[str, Set[str]] = {
    "pending": {"running", "skipped", "cancelled"},
    "running": {"completed", "failed", "awaiting_approval", "cancelled"},
    "awaiting_approval": {"running", "cancelled"},
    "completed": set(),
    "failed": {"pending"},
    "skipped": set(),
    "cancelled": set(),
}


class StateMachineError(Exception):
    """Raised when an invalid state transition is attempted."""
    def __init__(self, entity: str, current: str, target: str):
        self.entity = entity
        self.current = current
        self.target = target
        super().__init__(f"Invalid transition: {entity} from '{current}' to '{target}'")


def validate_execution_transition(current: str, target: str) -> None:
    allowed = EXECUTION_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise StateMachineError("PipelineExecution", current, target)


def validate_node_transition(current: str, target: str) -> None:
    allowed = NODE_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise StateMachineError("NodeExecution", current, target)


def create_execution(
    db: Session,
    project_id: int,
    pipeline_template_id: int,
    template_version: int,
    template_snapshot: Dict[str, Any],
    requested_by: int,
    idempotency_key: Optional[str] = None,
) -> PipelineExecution:
    """Create a new pipeline execution with idempotency support."""
    if idempotency_key:
        existing = (
            db.query(PipelineExecution)
            .filter(PipelineExecution.idempotency_key == idempotency_key)
            .first()
        )
        if existing:
            return existing

    execution = PipelineExecution(
        project_id=project_id,
        pipeline_template_id=pipeline_template_id,
        template_version=template_version,
        template_snapshot=json.dumps(template_snapshot),
        status="queued",
        idempotency_key=idempotency_key,
        requested_by=requested_by,
        created_at=datetime.now(timezone.utc),
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    return execution


def claim_execution(db: Session, execution_id: int) -> Optional[PipelineExecution]:
    """Atomically claim a queued execution for processing."""
    execution = (
        db.query(PipelineExecution)
        .filter(
            PipelineExecution.id == execution_id,
            PipelineExecution.status == "queued",
        )
        .with_for_update(skip_locked=True)
        .first()
    )
    if not execution:
        return None
    validate_execution_transition(execution.status, "running")
    execution.status = "running"
    execution.started_at = datetime.now(timezone.utc)
    db.commit()
    return execution


def transition_execution(db: Session, execution_id: int, target_status: str,
                         error_message: Optional[str] = None) -> PipelineExecution:
    """Transition a pipeline execution to a new status."""
    execution = db.query(PipelineExecution).filter(PipelineExecution.id == execution_id).first()
    if not execution:
        raise ValueError(f"Execution {execution_id} not found")
    validate_execution_transition(execution.status, target_status)
    execution.status = target_status
    if target_status == "completed":
        execution.finished_at = datetime.now(timezone.utc)
    elif target_status == "failed":
        execution.finished_at = datetime.now(timezone.utc)
        execution.error_message = error_message
    elif target_status == "cancelled":
        execution.cancelled_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(execution)
    return execution


def create_node_execution(
    db: Session, execution_id: int, node_key: str, node_type: str,
    input_snapshot: Dict[str, Any], attempt: int = 1,
) -> NodeExecution:
    node_exec = NodeExecution(
        pipeline_execution_id=execution_id,
        node_key=node_key,
        node_type=node_type,
        status="pending",
        attempt=attempt,
        input_snapshot=json.dumps(input_snapshot),
        created_at=datetime.now(timezone.utc),
    )
    db.add(node_exec)
    db.commit()
    db.refresh(node_exec)
    return node_exec


def transition_node(db: Session, node_execution_id: int, target_status: str,
                    output_snapshot: Optional[Dict] = None,
                    error_type: Optional[str] = None,
                    error_message: Optional[str] = None,
                    tokens: Optional[Dict[str, int]] = None,
                    duration_ms: Optional[int] = None) -> NodeExecution:
    node_exec = db.query(NodeExecution).filter(NodeExecution.id == node_execution_id).first()
    if not node_exec:
        raise ValueError(f"NodeExecution {node_execution_id} not found")
    validate_node_transition(node_exec.status, target_status)
    node_exec.status = target_status
    if output_snapshot:
        node_exec.output_snapshot = json.dumps(output_snapshot)
    if error_type:
        node_exec.error_type = error_type
    if error_message:
        node_exec.error_message = error_message
    if duration_ms:
        node_exec.duration_ms = duration_ms
    if tokens:
        node_exec.prompt_tokens = tokens.get("prompt_tokens", 0)
        node_exec.completion_tokens = tokens.get("completion_tokens", 0)
        node_exec.total_tokens = tokens.get("total_tokens", 0)
    if target_status == "running":
        node_exec.started_at = datetime.now(timezone.utc)
    elif target_status in ("completed", "failed"):
        node_exec.finished_at = datetime.now(timezone.utc)
        if not node_exec.started_at:
            node_exec.started_at = node_exec.finished_at
    db.commit()
    db.refresh(node_exec)
    return node_exec


def get_node_executions_for_execution(db: Session, execution_id: int) -> List[NodeExecution]:
    """Get all node executions for a pipeline execution."""
    return (
        db.query(NodeExecution)
        .filter(NodeExecution.pipeline_execution_id == execution_id)
        .order_by(NodeExecution.created_at.asc())
        .all()
    )


def get_ordered_nodes(template_snapshot: Dict[str, Any]) -> List[str]:
    """Get nodes in topological execution order."""
    nodes = template_snapshot.get("nodes", [])
    edges = template_snapshot.get("edges", [])
    return topological_sort(nodes, edges)

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class NodeExecution(Base):
    """Tracks the execution of a single node within a pipeline run."""

    __tablename__ = "node_executions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pipeline_execution_id: Mapped[int] = mapped_column(
        ForeignKey("pipeline_executions.id"), nullable=False, index=True
    )
    node_key: Mapped[str] = mapped_column(String(255), nullable=False)
    node_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )
    attempt: Mapped[int] = mapped_column(Integer, default=1)
    input_snapshot: Mapped[str] = mapped_column(Text, nullable=True, default="{}")
    output_snapshot: Mapped[str] = mapped_column(Text, nullable=True, default="{}")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    error_type: Mapped[str] = mapped_column(String(50), nullable=True, default=None)
    error_message: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    retryable: Mapped[bool] = mapped_column(Boolean, default=True)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<NodeExecution(id={self.id}, node={self.node_key!r}, status={self.status!r})>"

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class ApprovalRequest(Base):
    """Represents a human approval gate in a pipeline execution."""

    __tablename__ = "approval_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    execution_id: Mapped[int] = mapped_column(ForeignKey("pipeline_executions.id"), nullable=False, index=True)
    node_execution_id: Mapped[int] = mapped_column(
        ForeignKey("node_executions.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="pending", index=True
    )
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    decision: Mapped[str] = mapped_column(String(30), nullable=True, default=None)
    comment: Mapped[str] = mapped_column(Text, nullable=True, default=None)

    def __repr__(self) -> str:
        return f"<ApprovalRequest(id={self.id}, status={self.status!r})>"

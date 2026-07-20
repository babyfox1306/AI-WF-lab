from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class PipelineExecution(Base):
    """Represents one run of a pipeline template."""

    __tablename__ = "pipeline_executions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("opportunity_projects.id"), nullable=False, index=True)
    pipeline_template_id: Mapped[int] = mapped_column(ForeignKey("pipeline_templates.id"), nullable=False)
    template_version: Mapped[int] = mapped_column(Integer, default=1)
    template_snapshot: Mapped[str] = mapped_column(Text, nullable=True, default="{}")
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="queued", index=True
    )
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=True, unique=True, index=True)
    requested_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    current_node_key: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<PipelineExecution(id={self.id}, status={self.status!r})>"

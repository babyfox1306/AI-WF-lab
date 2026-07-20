from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Artifact(Base):
    """Stores intermediate and final outputs from pipeline executions."""

    __tablename__ = "artifacts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("opportunity_projects.id"), nullable=False, index=True)
    execution_id: Mapped[int] = mapped_column(ForeignKey("pipeline_executions.id"), nullable=False, index=True)
    node_execution_id: Mapped[int] = mapped_column(
        ForeignKey("node_executions.id"), nullable=True
    )
    artifact_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="generic"
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    content_text: Mapped[str] = mapped_column(Text, nullable=True)
    content_json: Mapped[str] = mapped_column(Text, nullable=True, default="{}")
    version: Mapped[int] = mapped_column(Integer, default=1)
    checksum: Mapped[str] = mapped_column(String(64), nullable=True)
    is_final: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Artifact(id={self.id}, type={self.artifact_type!r}, final={self.is_final})>"

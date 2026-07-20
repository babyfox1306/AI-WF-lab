from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Job(Base):
    """SQLAlchemy model representing a job execution."""

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflows.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    input_data: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    output_data: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )
    error_message: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    workflow = relationship("Workflow", backref="jobs")

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, name={self.name!r}, status={self.status!r})>"

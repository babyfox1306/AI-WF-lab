from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class GroundTruthRegistry(Base):
    """Registry of verified facts and constraints that agents must respect."""

    __tablename__ = "ground_truth_registry"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("opportunity_projects.id"), nullable=False, index=True)
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, default="job_requirement"
    )
    source_document_id: Mapped[int] = mapped_column(
        ForeignKey("source_documents.id"), nullable=True
    )
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    locked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<GroundTruthRegistry(id={self.id}, key={self.key!r}, locked={self.locked})>"

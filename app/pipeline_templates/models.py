from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class PipelineTemplate(Base):
    """A reusable versioned pipeline graph definition."""

    __tablename__ = "pipeline_templates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True, default="")
    version: Mapped[int] = mapped_column(Integer, default=1)
    graph_definition: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    input_schema: Mapped[str] = mapped_column(Text, nullable=True, default="{}")
    output_schema: Mapped[str] = mapped_column(Text, nullable=True, default="{}")
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
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
        return f"<PipelineTemplate(id={self.id}, slug={self.slug!r}, v{self.version})>"

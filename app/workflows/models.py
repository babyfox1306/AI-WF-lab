from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Workflow(Base):
    """SQLAlchemy model representing an AI workflow."""

    __tablename__ = "workflows"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True, default="")
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="draft", index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    workspace = relationship("Workspace", backref="workflows")

    def __repr__(self) -> str:
        return f"<Workflow(id={self.id}, name={self.name!r}, status={self.status!r})>"

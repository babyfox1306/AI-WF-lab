import hashlib
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class SourceDocument(Base):
    """Stores input material for analysis."""

    __tablename__ = "source_documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), nullable=False, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("opportunity_projects.id"), nullable=True, index=True)
    source_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="generic_text"
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    structured_data: Mapped[str] = mapped_column(Text, nullable=True, default="{}")
    checksum: Mapped[str] = mapped_column(String(64), nullable=True, index=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    workspace = relationship("Workspace", backref="source_documents")

    def __repr__(self) -> str:
        return f"<SourceDocument(id={self.id}, title={self.title!r}, type={self.source_type!r})>"

    @staticmethod
    def compute_checksum(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class ToolDefinition(Base):
    """Represents an external or internal tool that an agent may use."""

    __tablename__ = "tool_definitions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True, default="")
    tool_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="http"
    )
    endpoint: Mapped[str] = mapped_column(String(512), nullable=True, default=None)
    http_method: Mapped[str] = mapped_column(String(10), default="POST")
    request_schema: Mapped[str] = mapped_column(Text, nullable=True, default="{}")
    response_schema: Mapped[str] = mapped_column(Text, nullable=True, default="{}")
    headers_config: Mapped[str] = mapped_column(Text, nullable=True, default="{}")
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=30)
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

    workspace = relationship("Workspace", backref="tool_definitions")

    def __repr__(self) -> str:
        return f"<ToolDefinition(id={self.id}, slug={self.slug!r}, type={self.tool_type!r})>"

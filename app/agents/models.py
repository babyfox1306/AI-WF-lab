from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class AgentDefinition(Base):
    """Represents a reusable AI worker definition."""

    __tablename__ = "agent_definitions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True, default="")
    role: Mapped[str] = mapped_column(String(255), nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    provider_connection_id: Mapped[int] = mapped_column(ForeignKey("provider_connections.id"), nullable=True)
    model_override: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    max_output_tokens: Mapped[int] = mapped_column(Integer, default=4096)
    tools_config: Mapped[str] = mapped_column(Text, nullable=True, default="{}")
    output_schema: Mapped[str] = mapped_column(Text, nullable=True, default="{}")
    version: Mapped[int] = mapped_column(Integer, default=1)
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

    workspace = relationship("Workspace", backref="agent_definitions")

    def __repr__(self) -> str:
        return f"<AgentDefinition(id={self.id}, slug={self.slug!r}, v{self.version})>"

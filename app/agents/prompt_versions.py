from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class PromptTemplateVersion(Base):
    """Stores prompt versions separately from mutable agent configuration."""

    __tablename__ = "prompt_template_versions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    agent_definition_id: Mapped[int] = mapped_column(
        ForeignKey("agent_definitions.id"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    user_prompt_template: Mapped[str] = mapped_column(Text, nullable=True, default="")
    output_schema: Mapped[str] = mapped_column(Text, nullable=True, default="{}")
    checksum: Mapped[str] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<PromptTemplateVersion(id={self.id}, agent={self.agent_definition_id}, v{self.version})>"

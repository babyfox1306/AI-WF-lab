from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Log(Base):
    """SQLAlchemy model representing a job execution log."""

    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False, index=True)
    level: Mapped[str] = mapped_column(
        String(20), nullable=False, default="info", index=True
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    job = relationship("Job", backref="logs")

    def __repr__(self) -> str:
        return f"<Log(id={self.id}, level={self.level!r}, message={self.message[:50]!r})>"

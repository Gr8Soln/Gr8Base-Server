import uuid

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class ProjectModel(Base):
    __tablename__ = "career_projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    role: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    technologies: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    responsibilities: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    repository: Mapped[str] = mapped_column(String(1000), default="", nullable=False)
    demo_url: Mapped[str] = mapped_column(String(1000), default="", nullable=False)
    url: Mapped[str] = mapped_column(String(1000), default="", nullable=False)
    duration: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    impact: Mapped[str] = mapped_column(Text, default="", nullable=False)
    ai_summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

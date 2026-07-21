import uuid

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class ExperienceModel(Base):
    __tablename__ = "career_experiences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company: Mapped[str] = mapped_column(String(500), nullable=False)
    role: Mapped[str] = mapped_column(String(500), nullable=False)
    start_date: Mapped[str] = mapped_column(String(50), nullable=False)
    end_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    location: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    employment_type: Mapped[str] = mapped_column(String(50), default="full_time", nullable=False)
    industry: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    company_website: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    responsibilities: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    achievements: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    technologies: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    impact_statements: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    related_projects: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    ai_summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(nullable=True)
    enrichment_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

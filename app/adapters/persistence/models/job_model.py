import uuid

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class JobModel(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    raw_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    title: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    company: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    company_url: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    location: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    work_type: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    role: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    seniority: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    domain: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    required_skills: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    preferred_skills: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    soft_skills: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    tools_and_technologies: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    ats_keywords: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    hidden_signals: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # embedding column added via migration 0003
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

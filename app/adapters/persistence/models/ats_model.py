import uuid

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class ATSScoreModel(Base):
    __tablename__ = "ats_scores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    dimensions: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    dimension_breakdown: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    missing_keywords: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    weak_sections: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    recommendations: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    recruiter_critique: Mapped[str] = mapped_column(Text, nullable=False, default="")
    is_ats_safe: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    safety_issues: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

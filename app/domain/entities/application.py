import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.enums.application_stage import ApplicationStage


@dataclass
class ApplicationNote:
    content: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class JobApplication:
    user_id: uuid.UUID
    job_title: str
    company: str
    stage: ApplicationStage = ApplicationStage.SAVED
    job_id: uuid.UUID | None = None
    resume_id: uuid.UUID | None = None
    cover_letter_id: uuid.UUID | None = None
    job_url: str = ""
    recruiter_name: str = ""
    recruiter_email: str = ""
    recruiter_linkedin: str = ""
    salary_min: int | None = None
    salary_max: int | None = None
    applied_at: datetime | None = None
    interview_date: datetime | None = None
    deadline: datetime | None = None
    rejection_reason: str = ""
    outcome_notes: str = ""
    notes: list[ApplicationNote] = field(default_factory=list)
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

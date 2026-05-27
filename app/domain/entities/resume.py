import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.enums.resume_strategy import ResumeStrategy


@dataclass
class ImpactStatement:
    problem: str
    solution: str
    result: str
    metric: str = ""


@dataclass
class WorkExperience:
    company: str
    role: str
    start_date: str
    end_date: str | None
    is_current: bool = False
    location: str = ""
    description: str = ""
    impact_statements: list[ImpactStatement] = field(default_factory=list)
    technologies: list[str] = field(default_factory=list)
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Project:
    name: str
    description: str
    technologies: list[str] = field(default_factory=list)
    url: str = ""
    impact: str = ""
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Education:
    institution: str
    degree: str
    field_of_study: str
    start_year: int | None = None
    end_year: int | None = None
    gpa: float | None = None
    honors: str = ""
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Certification:
    name: str
    issuer: str
    issue_date: str = ""
    expiry_date: str = ""
    credential_url: str = ""
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Resume:
    user_id: uuid.UUID
    file_url: str
    file_name: str
    raw_text: str
    skills: list[str] = field(default_factory=list)
    experience: list[WorkExperience] = field(default_factory=list)
    projects: list[Project] = field(default_factory=list)
    education: list[Education] = field(default_factory=list)
    certifications: list[Certification] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    embedding: list[float] | None = None
    version: int = 1
    label: str = ""
    strategy: ResumeStrategy | None = None
    parent_resume_id: uuid.UUID | None = None  # for versioning
    ats_score_snapshot: float | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

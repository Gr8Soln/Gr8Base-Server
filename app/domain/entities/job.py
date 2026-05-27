import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class JobRequirement:
    skill: str
    is_required: bool = True
    proficiency: str = ""


@dataclass
class JobDescription:
    user_id: uuid.UUID
    raw_text: str
    title: str = ""
    company: str = ""
    company_url: str = ""
    location: str = ""
    work_type: str = ""
    role: str = ""
    seniority: str = ""
    domain: str = ""
    required_skills: list[str] = field(default_factory=list)
    preferred_skills: list[str] = field(default_factory=list)
    soft_skills: list[str] = field(default_factory=list)
    tools_and_technologies: list[str] = field(default_factory=list)
    ats_keywords: list[str] = field(default_factory=list)
    hidden_signals: list[str] = field(default_factory=list)
    salary_min: int | None = None
    salary_max: int | None = None
    embedding: list[float] | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

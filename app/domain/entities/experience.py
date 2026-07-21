import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.enums.employment_type import EmploymentType


@dataclass
class ImpactStatement:
    problem: str
    solution: str
    result: str
    metric: str = ""


@dataclass
class WorkExperience:
    """Canonical work experience entity for the Career Profile Engine.

    This is the source-of-truth entity. The resume-level WorkExperience
    in resume.py is a derived artifact used only for resume rendering.
    """

    user_id: uuid.UUID
    company: str
    role: str
    start_date: str
    end_date: str | None = None
    is_current: bool = False
    location: str = ""
    description: str = ""
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    industry: str = ""
    company_website: str = ""
    responsibilities: list[str] = field(default_factory=list)
    achievements: list[str] = field(default_factory=list)
    technologies: list[str] = field(default_factory=list)
    impact_statements: list[ImpactStatement] = field(default_factory=list)
    related_projects: list[uuid.UUID] = field(default_factory=list)
    ai_summary: str = ""
    embedding: list[float] | None = None
    enrichment_data: dict = field(default_factory=dict)
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

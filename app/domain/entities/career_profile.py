import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class CareerProfile:
    """Canonical career profile — the single source of truth.

    This extends the basic CareerProfile in user.py with additional
    fields for the Career Profile Engine. The existing CareerProfile
    in user.py remains for basic profile operations.

    Personal information and professional summary live here.
    Experiences, projects, skills, etc. are separate entities
    linked by user_id.
    """

    user_id: uuid.UUID
    full_name: str
    email: str
    headline: str = ""
    summary: str = ""
    location: str = ""
    phone: str = ""
    address: str = ""
    linkedin_url: str = ""
    github_url: str = ""
    portfolio_url: str = ""
    website: str = ""
    years_of_experience: int = 0
    target_roles: list[str] = field(default_factory=list)
    target_industries: list[str] = field(default_factory=list)
    target_salary_min: int | None = None
    target_salary_max: int | None = None
    preferred_work_type: str = ""
    writing_tone: str = "professional"
    summary_embedding: list[float] | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

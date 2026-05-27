import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class CareerProfile:
    user_id: uuid.UUID
    full_name: str
    email: str
    headline: str = ""
    summary: str = ""
    location: str = ""
    phone: str = ""
    linkedin_url: str = ""
    github_url: str = ""
    portfolio_url: str = ""
    years_of_experience: int = 0
    target_roles: list[str] = field(default_factory=list)
    target_industries: list[str] = field(default_factory=list)
    target_salary_min: int | None = None
    target_salary_max: int | None = None
    preferred_work_type: str = ""  # remote, hybrid, onsite
    writing_tone: str = "professional"
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class User:
    email: str
    hashed_password: str
    full_name: str
    is_active: bool = True
    is_verified: bool = False
    is_superuser: bool = False
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

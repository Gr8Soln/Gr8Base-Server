import enum
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


class AuthProvider(enum.Enum):
    GOOGLE = "google"

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
    full_name: str
    hashed_password: str = ""
    auth_provider: AuthProvider = AuthProvider.GOOGLE
    is_active: bool = True
    is_verified: bool = False
    is_superuser: bool = False
    avatar_url: str = ""
    google_sub: str = ""
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @staticmethod
    def create_google_user(
        email: str,
        full_name: str,
        google_sub: str,
        avatar_url: str = ""
    ):
        return User(
            email=email,
            full_name=full_name,
            google_sub=google_sub,
            avatar_url=avatar_url,
            auth_provider=AuthProvider.GOOGLE,
            is_verified=True
        )

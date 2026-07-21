import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class Education:
    """Canonical education entity for the Career Profile Engine."""

    user_id: uuid.UUID
    institution: str
    degree: str
    field_of_study: str = ""
    start_year: int | None = None
    end_year: int | None = None
    gpa: float | None = None
    honors: str = ""
    activities: str = ""
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

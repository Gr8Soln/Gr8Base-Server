import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class Project:
    """Canonical project entity for the Career Profile Engine."""

    user_id: uuid.UUID
    name: str
    description: str
    role: str = ""
    technologies: list[str] = field(default_factory=list)
    responsibilities: list[str] = field(default_factory=list)
    repository: str = ""
    demo_url: str = ""
    url: str = ""
    duration: str = ""
    impact: str = ""
    ai_summary: str = ""
    embedding: list[float] | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

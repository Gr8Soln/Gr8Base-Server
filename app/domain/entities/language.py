import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class Language:
    """Canonical language entity for the Career Profile Engine."""

    user_id: uuid.UUID
    name: str
    proficiency: str = ""  # e.g. "native", "fluent", "intermediate", "basic"
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

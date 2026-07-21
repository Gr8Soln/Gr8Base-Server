import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class Award:
    """Canonical award entity for the Career Profile Engine."""

    user_id: uuid.UUID
    name: str
    issuer: str
    date: str = ""
    description: str = ""
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

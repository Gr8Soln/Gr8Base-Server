import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class Certification:
    """Canonical certification entity for the Career Profile Engine."""

    user_id: uuid.UUID
    name: str
    issuer: str
    issue_date: str = ""
    expiry_date: str = ""
    credential_url: str = ""
    credential_id: str = ""
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

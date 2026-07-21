import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.enums.skill_category import SkillCategory


@dataclass
class Technology:
    """Technology/tool entity grouped by category."""

    user_id: uuid.UUID
    name: str
    category: SkillCategory = SkillCategory.TOOL
    proficiency: str = ""
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

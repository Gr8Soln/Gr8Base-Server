import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.enums.skill_category import SkillCategory


@dataclass
class Skill:
    """Canonical skill entity for the Career Profile Engine"""

    user_id: uuid.UUID
    name: str
    category: SkillCategory = SkillCategory.TECHNICAL
    proficiency: str = ""  # e.g. "beginner", "intermediate", "advanced", "expert"
    years_of_experience: float = 0.0
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

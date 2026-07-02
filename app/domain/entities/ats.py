import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class ScoreDimension:
    name: str
    score: float  # 0.0 – 1.0
    weight: float  # contribution to overall
    feedback: str = ""
    suggestions: list[str] = field(default_factory=list)


@dataclass
class ATSScore:
    resume_id: uuid.UUID
    job_id: uuid.UUID
    user_id: uuid.UUID
    overall_score: float  # 0.0 – 100.0
    dimensions: list[ScoreDimension] = field(default_factory=list)
    missing_keywords: list[str] = field(default_factory=list)
    weak_sections: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    recruiter_critique: str = ""
    is_ats_safe: bool = True
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

from typing import TypedDict


class ATSScoringState(TypedDict):
    # Inputs
    user_id: str
    resume_id: str
    job_id: str
    resume_data: dict
    job_data: dict

    # Keyword match node
    keyword_score: float
    keyword_matches: list[str]
    keyword_gaps: list[str]

    # Semantic match node
    semantic_score: float
    semantic_gaps: list[str]

    # Technical alignment node
    technical_score: float
    technical_feedback: str

    # Individual dimension scores
    seniority_score: float
    impact_score: float
    ats_safety_score: float
    readability_score: float
    density_score: float
    role_alignment_score: float
    repetition_penalty: float

    # ATS safety
    is_ats_safe: bool
    safety_issues: list[str]

    # Final output
    overall_score: float
    dimension_breakdown: dict
    recommendations: list[str]
    missing_skills: list[str]
    weak_sections: list[str]
    recruiter_critique: str

    # Control
    errors: list[str]

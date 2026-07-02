from pydantic import BaseModel


class ScoreDimensionResponse(BaseModel):
    name: str
    score: float
    weight: float
    feedback: str
    suggestions: list[str]


class ATSScoreResponse(BaseModel):
    id: str
    resume_id: str
    job_id: str
    overall_score: float
    dimensions: list[ScoreDimensionResponse]
    missing_keywords: list[str]
    weak_sections: list[str]
    recommendations: list[str]
    recruiter_critique: str
    is_ats_safe: bool


class ScoreRequest(BaseModel):
    resume_id: str
    job_id: str


class ScoreTaskResponse(BaseModel):
    task_id: str
    resume_id: str
    job_id: str
    status: str = "queued"
    message: str = "ATS scoring queued. Poll /ats/scores/{score_id} for results."

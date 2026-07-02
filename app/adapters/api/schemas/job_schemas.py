from pydantic import BaseModel


class AnalyzeJobRequest(BaseModel):
    raw_text: str
    company: str = ""
    company_url: str = ""


class JobResponse(BaseModel):
    id: str
    user_id: str
    title: str
    company: str
    company_url: str
    location: str
    work_type: str
    role: str
    seniority: str
    domain: str
    required_skills: list[str]
    preferred_skills: list[str]
    soft_skills: list[str]
    tools_and_technologies: list[str]
    ats_keywords: list[str]
    hidden_signals: list[str]
    salary_min: int | None
    salary_max: int | None


class KeywordsResponse(BaseModel):
    job_id: str
    keywords: list[str]
    total: int

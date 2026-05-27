
from pydantic import BaseModel


class ImpactStatementResponse(BaseModel):
    problem: str
    solution: str
    result: str
    metric: str


class WorkExperienceResponse(BaseModel):
    id: str
    company: str
    role: str
    start_date: str
    end_date: str | None
    is_current: bool
    location: str
    description: str
    technologies: list[str]
    impact_statements: list[ImpactStatementResponse]


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    technologies: list[str]
    url: str
    impact: str


class EducationResponse(BaseModel):
    id: str
    institution: str
    degree: str
    field_of_study: str
    start_year: int | None
    end_year: int | None
    gpa: float | None
    honors: str


class CertificationResponse(BaseModel):
    id: str
    name: str
    issuer: str
    issue_date: str
    expiry_date: str
    credential_url: str


class ResumeResponse(BaseModel):
    id: str
    user_id: str
    file_name: str
    file_url: str
    version: int
    label: str
    strategy: str | None
    ats_score_snapshot: float | None
    skills: list[str]
    experience: list[WorkExperienceResponse]
    projects: list[ProjectResponse]
    education: list[EducationResponse]
    certifications: list[CertificationResponse]
    languages: list[str]
    created_at: str | None = None


class ResumeUploadResponse(BaseModel):
    id: str
    user_id: str
    file_name: str
    status: str = "uploaded"
    message: str = "Resume uploaded. Parsing in progress."


class ResumeLabelUpdateRequest(BaseModel):
    label: str


class OptimizeResumeRequest(BaseModel):
    job_id: str
    strategy: str = "ats_aggressive"
    label: str = ""


class OptimizeResumeResponse(BaseModel):
    task_id: str
    resume_id: str
    job_id: str
    strategy: str
    status: str = "queued"
    message: str = "Optimization queued. Poll GET /resumes/{id} for the new version."


class ResumeComparisonResponse(BaseModel):
    base_id: str
    optimized_id: str
    added_skills: list[str]
    removed_skills: list[str]
    ats_score_delta: float | None
    experience_delta: int


class PDFRenderRequest(BaseModel):
    template: str = "classic"


class PDFRenderResponse(BaseModel):
    task_id: str
    resume_id: str
    template: str
    status: str = "queued"
    message: str = "PDF rendering queued."

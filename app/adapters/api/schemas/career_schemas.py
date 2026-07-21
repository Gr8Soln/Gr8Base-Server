from pydantic import BaseModel, Field


# ── Profile ───────────────────────────────────────────────────────────────────


class CareerProfileResponse(BaseModel):
    id: str
    user_id: str
    full_name: str
    email: str
    headline: str = ""
    summary: str = ""
    location: str = ""
    phone: str = ""
    address: str = ""
    linkedin_url: str = ""
    github_url: str = ""
    portfolio_url: str = ""
    website: str = ""
    years_of_experience: int = 0
    target_roles: list[str] = []
    target_industries: list[str] = []
    target_salary_min: int | None = None
    target_salary_max: int | None = None
    preferred_work_type: str = ""
    writing_tone: str = "professional"
    created_at: str = ""
    updated_at: str = ""

    model_config = {"from_attributes": True}


class UpdateCareerProfileRequest(BaseModel):
    full_name: str | None = None
    headline: str | None = None
    summary: str | None = None
    location: str | None = None
    phone: str | None = None
    address: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None
    website: str | None = None
    years_of_experience: int | None = None
    target_roles: list[str] | None = None
    target_industries: list[str] | None = None
    preferred_work_type: str | None = None
    writing_tone: str | None = None


# ── Sub-entity Responses ──────────────────────────────────────────────────────


class ImpactStatementResponse(BaseModel):
    problem: str = ""
    solution: str = ""
    result: str = ""
    metric: str = ""


class ExperienceResponse(BaseModel):
    id: str
    user_id: str
    company: str
    role: str
    start_date: str
    end_date: str | None = None
    is_current: bool = False
    location: str = ""
    description: str = ""
    employment_type: str = "full_time"
    industry: str = ""
    company_website: str = ""
    responsibilities: list[str] = []
    achievements: list[str] = []
    technologies: list[str] = []
    impact_statements: list[ImpactStatementResponse] = []
    ai_summary: str = ""


class ProjectResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: str = ""
    role: str = ""
    technologies: list[str] = []
    responsibilities: list[str] = []
    repository: str = ""
    demo_url: str = ""
    url: str = ""
    duration: str = ""
    impact: str = ""
    ai_summary: str = ""


class SkillResponse(BaseModel):
    id: str
    user_id: str
    name: str
    category: str = "technical"
    proficiency: str = ""
    years_of_experience: float = 0.0


class TechnologyResponse(BaseModel):
    id: str
    user_id: str
    name: str
    category: str = "tool"
    proficiency: str = ""


class EducationResponse(BaseModel):
    id: str
    user_id: str
    institution: str
    degree: str
    field_of_study: str = ""
    start_year: int | None = None
    end_year: int | None = None
    gpa: float | None = None
    honors: str = ""
    activities: str = ""


class CertificationResponse(BaseModel):
    id: str
    user_id: str
    name: str
    issuer: str
    issue_date: str = ""
    expiry_date: str = ""
    credential_url: str = ""
    credential_id: str = ""


class AwardResponse(BaseModel):
    id: str
    user_id: str
    name: str
    issuer: str
    date: str = ""
    description: str = ""


class PublicationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    publisher: str
    date: str = ""
    url: str = ""
    description: str = ""


class BlogResponse(BaseModel):
    id: str
    user_id: str
    title: str
    url: str
    platform: str = ""
    date: str = ""
    description: str = ""


class LanguageResponse(BaseModel):
    id: str
    user_id: str
    name: str
    proficiency: str = ""


# ── Full Profile ──────────────────────────────────────────────────────────────


class FullCareerProfileResponse(BaseModel):
    profile: CareerProfileResponse
    experiences: list[ExperienceResponse] = []
    projects: list[ProjectResponse] = []
    skills: list[SkillResponse] = []
    technologies: list[TechnologyResponse] = []
    education: list[EducationResponse] = []
    certifications: list[CertificationResponse] = []
    awards: list[AwardResponse] = []
    publications: list[PublicationResponse] = []
    blogs: list[BlogResponse] = []
    languages: list[LanguageResponse] = []


# ── Ingestion ─────────────────────────────────────────────────────────────────


class IngestResumeResponse(BaseModel):
    workflow_id: str
    status: str
    file_url: str


class IngestionStatusResponse(BaseModel):
    workflow_id: str
    status: str
    source_file_name: str = ""
    error_message: str = ""
    events: list[dict] = []
    created_at: str = ""
    updated_at: str = ""


# ── CRUD Requests ─────────────────────────────────────────────────────────────


class CreateEntityRequest(BaseModel):
    data: dict = Field(default_factory=dict)


class UpdateEntityRequest(BaseModel):
    data: dict = Field(default_factory=dict)

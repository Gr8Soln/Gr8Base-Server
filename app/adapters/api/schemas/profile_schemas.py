from pydantic import BaseModel


class ProfileResponse(BaseModel):
    id: str
    user_id: str
    full_name: str
    email: str
    headline: str
    summary: str
    location: str
    phone: str
    linkedin_url: str
    github_url: str
    portfolio_url: str
    years_of_experience: int
    target_roles: list[str]
    target_industries: list[str]
    target_salary_min: int | None
    target_salary_max: int | None
    preferred_work_type: str
    writing_tone: str


class UpdateProfileRequest(BaseModel):
    full_name: str | None = None
    headline: str | None = None
    summary: str | None = None
    location: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None
    years_of_experience: int | None = None
    target_roles: list[str] | None = None
    target_industries: list[str] | None = None
    target_salary_min: int | None = None
    target_salary_max: int | None = None
    preferred_work_type: str | None = None
    writing_tone: str | None = None

from pydantic import BaseModel, Field

from app.adapters.ai.prompts.career.extract_profile import (
    SYSTEM_PROMPT,
    build_extract_prompt,
)
from app.application.ports.ai.career_extractor_port import CareerExtractorPort
from app.domain.entities.career_profile import CareerProfile
from app.domain.exceptions.domain_exceptions import AIGenerationError
from app.infrastructure.llm.instructor_client import extract_structured
from app.infrastructure.observability.structlog_setup import get_logger

logger = get_logger(__name__)

# ── Pydantic schemas for structured LLM output ────────────────────────────────


class ExtractedImpact(BaseModel):
    problem: str = ""
    solution: str = ""
    result: str = ""
    metric: str = ""


class ExtractedExperience(BaseModel):
    company: str
    role: str
    start_date: str = ""
    end_date: str | None = None
    is_current: bool = False
    location: str = ""
    description: str = ""
    employment_type: str = "full_time"
    responsibilities: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    impact_statements: list[ExtractedImpact] = Field(default_factory=list)


class ExtractedProject(BaseModel):
    name: str
    description: str = ""
    role: str = ""
    technologies: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    repository: str = ""
    demo_url: str = ""
    url: str = ""
    duration: str = ""
    impact: str = ""


class ExtractedSkill(BaseModel):
    name: str
    category: str = "technical"
    proficiency: str = ""
    years_of_experience: float = 0.0


class ExtractedTechnology(BaseModel):
    name: str
    category: str = "tool"
    proficiency: str = ""


class ExtractedEducation(BaseModel):
    institution: str
    degree: str
    field_of_study: str = ""
    start_year: int | None = None
    end_year: int | None = None
    gpa: float | None = None
    honors: str = ""
    activities: str = ""


class ExtractedCertification(BaseModel):
    name: str
    issuer: str
    issue_date: str = ""
    expiry_date: str = ""
    credential_url: str = ""
    credential_id: str = ""


class ExtractedAward(BaseModel):
    name: str
    issuer: str
    date: str = ""
    description: str = ""


class ExtractedPublication(BaseModel):
    title: str
    publisher: str
    date: str = ""
    url: str = ""
    description: str = ""


class ExtractedBlog(BaseModel):
    title: str
    url: str
    platform: str = ""
    date: str = ""
    description: str = ""


class ExtractedLanguage(BaseModel):
    name: str
    proficiency: str = ""


class ExtractedProfile(BaseModel):
    """Personal information extracted from resume."""

    full_name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin_url: str = ""
    github_url: str = ""
    portfolio_url: str = ""
    website: str = ""
    headline: str = ""
    summary: str = ""
    years_of_experience: int = 0


class ExtractedCareerData(BaseModel):
    """Complete extracted career profile — all entities."""

    profile: ExtractedProfile = Field(default_factory=ExtractedProfile)
    experiences: list[ExtractedExperience] = Field(default_factory=list)
    projects: list[ExtractedProject] = Field(default_factory=list)
    skills: list[ExtractedSkill] = Field(default_factory=list)
    technologies: list[ExtractedTechnology] = Field(default_factory=list)
    education: list[ExtractedEducation] = Field(default_factory=list)
    certifications: list[ExtractedCertification] = Field(default_factory=list)
    awards: list[ExtractedAward] = Field(default_factory=list)
    publications: list[ExtractedPublication] = Field(default_factory=list)
    blogs: list[ExtractedBlog] = Field(default_factory=list)
    languages: list[ExtractedLanguage] = Field(default_factory=list)


# ── Agent ─────────────────────────────────────────────────────────────────────


class CareerExtractorAgent(CareerExtractorPort):
    """AI agent that extracts a complete career profile from raw resume text.

    Uses Instructor + LiteLLM for structured extraction with schema validation.
    """

    async def extract(self, raw_text: str, user_id: str, profile: CareerProfile) -> dict:
        logger.info("career_extractor_start", user_id=user_id)

        try:
            extracted: ExtractedCareerData = await extract_structured(
                response_model=ExtractedCareerData,
                messages=[{"role": "user", "content": build_extract_prompt(raw_text)}],
                system=SYSTEM_PROMPT,
                temperature=0.0,
            )
        except Exception as e:
            raise AIGenerationError("career_extractor", str(e)) from e

        # Update profile with extracted personal info
        p = extracted.profile
        profile.full_name = p.full_name or profile.full_name
        profile.email = p.email or profile.email
        profile.phone = p.phone or profile.phone
        profile.location = p.location or profile.location
        profile.linkedin_url = p.linkedin_url or profile.linkedin_url
        profile.github_url = p.github_url or profile.github_url
        profile.portfolio_url = p.portfolio_url or profile.portfolio_url
        profile.website = p.website or profile.website
        profile.headline = p.headline or profile.headline
        profile.summary = p.summary or profile.summary
        profile.years_of_experience = p.years_of_experience or profile.years_of_experience

        result = {
            "profile": profile,
            "experiences": [
                {
                    "company": e.company,
                    "role": e.role,
                    "start_date": e.start_date,
                    "end_date": e.end_date,
                    "is_current": e.is_current,
                    "location": e.location,
                    "description": e.description,
                    "employment_type": e.employment_type,
                    "responsibilities": e.responsibilities,
                    "achievements": e.achievements,
                    "technologies": e.technologies,
                    "impact_statements": [
                        {
                            "problem": i.problem,
                            "solution": i.solution,
                            "result": i.result,
                            "metric": i.metric,
                        }
                        for i in e.impact_statements
                    ],
                }
                for e in extracted.experiences
            ],
            "projects": [p.model_dump() for p in extracted.projects],
            "skills": [s.model_dump() for s in extracted.skills],
            "technologies": [t.model_dump() for t in extracted.technologies],
            "education": [e.model_dump() for e in extracted.education],
            "certifications": [c.model_dump() for c in extracted.certifications],
            "awards": [a.model_dump() for a in extracted.awards],
            "publications": [p.model_dump() for p in extracted.publications],
            "blogs": [b.model_dump() for b in extracted.blogs],
            "languages": [l.model_dump() for l in extracted.languages],
        }

        logger.info(
            "career_extractor_done",
            user_id=user_id,
            experiences=len(result["experiences"]),
            projects=len(result["projects"]),
            skills=len(result["skills"]),
        )
        return result

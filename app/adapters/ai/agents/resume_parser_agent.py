import uuid

from pydantic import BaseModel, Field

from app.adapters.ai.prompts.resume.parse_resume import SYSTEM_PROMPT, build_parse_prompt
from app.application.ports.ai.resume_parser_port import ResumeParserPort
from app.domain.entities.resume import (
    Certification,
    Education,
    ImpactStatement,
    Project,
    Resume,
    WorkExperience,
)
from app.domain.exceptions.domain_exceptions import AIGenerationError
from app.infrastructure.llm.instructor_client import extract_structured
from app.infrastructure.observability.structlog_setup import get_logger

logger = get_logger(__name__)


# ── Pydantic schemas for structured LLM output ────────────────────────────────

class ParsedImpact(BaseModel):
    problem: str = Field(default="", description="The problem or challenge faced")
    solution: str = Field(default="", description="Action taken or solution implemented")
    result: str = Field(default="", description="The outcome or result achieved")
    metric: str = Field(default="", description="Quantified metric if present, e.g. '40%', '$2M'")


class ParsedExperience(BaseModel):
    company: str
    role: str
    start_date: str = Field(description="Format: YYYY-MM or YYYY")
    end_date: str | None = Field(
        default=None, description="Format: YYYY-MM or YYYY, null if current"
    )
    is_current: bool = False
    location: str = ""
    description: str = ""
    technologies: list[str] = Field(default_factory=list)
    impact_statements: list[ParsedImpact] = Field(default_factory=list)


class ParsedProject(BaseModel):
    name: str
    description: str
    technologies: list[str] = Field(default_factory=list)
    url: str = ""
    impact: str = ""


class ParsedEducation(BaseModel):
    institution: str
    degree: str
    field_of_study: str = ""
    start_year: int | None = None
    end_year: int | None = None
    gpa: float | None = None
    honors: str = ""


class ParsedCertification(BaseModel):
    name: str
    issuer: str
    issue_date: str = ""
    expiry_date: str = ""
    credential_url: str = ""


class ParsedResume(BaseModel):
    skills: list[str] = Field(default_factory=list, description="All technical and soft skills")
    experience: list[ParsedExperience] = Field(default_factory=list)
    projects: list[ParsedProject] = Field(default_factory=list)
    education: list[ParsedEducation] = Field(default_factory=list)
    certifications: list[ParsedCertification] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list, description="Spoken/written languages")


# ── Agent ─────────────────────────────────────────────────────────────────────

class ResumeParserAgent(ResumeParserPort):
    async def parse(self, raw_text: str, resume: Resume) -> Resume:
        logger.info("resume_parser_agent_start", resume_id=str(resume.id))

        try:
            parsed: ParsedResume = await extract_structured(
                response_model=ParsedResume,
                messages=[{"role": "user", "content": build_parse_prompt(raw_text)}],
                system=SYSTEM_PROMPT,
                temperature=0.0,
            )
        except Exception as e:
            raise AIGenerationError("resume_parser_agent", str(e)) from e

        resume.skills = parsed.skills
        resume.languages = parsed.languages

        resume.experience = [
            WorkExperience(
                id=uuid.uuid4(),
                company=exp.company,
                role=exp.role,
                start_date=exp.start_date,
                end_date=exp.end_date,
                is_current=exp.is_current,
                location=exp.location,
                description=exp.description,
                technologies=exp.technologies,
                impact_statements=[
                    ImpactStatement(
                        problem=i.problem,
                        solution=i.solution,
                        result=i.result,
                        metric=i.metric,
                    )
                    for i in exp.impact_statements
                ],
            )
            for exp in parsed.experience
        ]

        resume.projects = [
            Project(
                id=uuid.uuid4(),
                name=p.name,
                description=p.description,
                technologies=p.technologies,
                url=p.url,
                impact=p.impact,
            )
            for p in parsed.projects
        ]

        resume.education = [
            Education(
                id=uuid.uuid4(),
                institution=e.institution,
                degree=e.degree,
                field_of_study=e.field_of_study,
                start_year=e.start_year,
                end_year=e.end_year,
                gpa=e.gpa,
                honors=e.honors,
            )
            for e in parsed.education
        ]

        resume.certifications = [
            Certification(
                id=uuid.uuid4(),
                name=c.name,
                issuer=c.issuer,
                issue_date=c.issue_date,
                expiry_date=c.expiry_date,
                credential_url=c.credential_url,
            )
            for c in parsed.certifications
        ]

        logger.info(
            "resume_parser_agent_done",
            resume_id=str(resume.id),
            skills=len(resume.skills),
            experience=len(resume.experience),
            projects=len(resume.projects),
        )
        return resume

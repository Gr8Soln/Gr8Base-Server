from pydantic import BaseModel, Field

from app.adapters.ai.prompts.jd.analyze_jd import SYSTEM_PROMPT, build_analyze_jd_prompt
from app.application.ports.ai.jd_analyzer_port import JDAnalyzerPort
from app.domain.entities.job import JobDescription
from app.domain.exceptions.domain_exceptions import AIGenerationError
from app.infrastructure.llm.instructor_client import extract_structured
from app.infrastructure.observability.structlog_setup import get_logger

logger = get_logger(__name__)


class ParsedJobDescription(BaseModel):
    title: str = ""
    company: str = ""
    location: str = ""
    work_type: str = Field(
        default="", description="remote | hybrid | onsite | not_specified"
    )
    role: str = Field(default="", description="Normalized role category e.g. Backend Engineer")
    seniority: str = Field(
        default="",
        description="Junior | Mid-Level | Senior | Staff | Principal | Lead | Manager",
    )
    domain: str = Field(
        default="", description="Industry domain e.g. Fintech, SaaS, Healthcare, E-commerce"
    )
    required_skills: list[str] = Field(
        default_factory=list,
        description="Skills explicitly required or must-have",
    )
    preferred_skills: list[str] = Field(
        default_factory=list,
        description="Skills listed as nice-to-have or preferred",
    )
    soft_skills: list[str] = Field(
        default_factory=list,
        description="Communication, leadership, collaboration traits mentioned",
    )
    tools_and_technologies: list[str] = Field(
        default_factory=list,
        description="All specific tools, frameworks, platforms mentioned",
    )
    ats_keywords: list[str] = Field(
        default_factory=list,
        description="High-value ATS keywords a recruiter would filter on",
    )
    hidden_signals: list[str] = Field(
        default_factory=list,
        description="Implicit expectations, culture signals, unstated requirements",
    )
    salary_min: int | None = Field(default=None, description="Minimum salary if mentioned")
    salary_max: int | None = Field(default=None, description="Maximum salary if mentioned")


class JDAnalyzerAgent(JDAnalyzerPort):
    async def analyze(self, raw_text: str, job: JobDescription) -> JobDescription:
        logger.info("jd_analyzer_agent_start", job_id=str(job.id))

        try:
            parsed: ParsedJobDescription = await extract_structured(
                response_model=ParsedJobDescription,
                messages=[{"role": "user", "content": build_analyze_jd_prompt(raw_text)}],
                system=SYSTEM_PROMPT,
                temperature=0.0,
            )
        except Exception as e:
            raise AIGenerationError("jd_analyzer_agent", str(e)) from e

        job.title = parsed.title
        job.company = parsed.company
        job.location = parsed.location
        job.work_type = parsed.work_type
        job.role = parsed.role
        job.seniority = parsed.seniority
        job.domain = parsed.domain
        job.required_skills = parsed.required_skills
        job.preferred_skills = parsed.preferred_skills
        job.soft_skills = parsed.soft_skills
        job.tools_and_technologies = parsed.tools_and_technologies
        job.ats_keywords = parsed.ats_keywords
        job.hidden_signals = parsed.hidden_signals
        job.salary_min = parsed.salary_min
        job.salary_max = parsed.salary_max

        logger.info(
            "jd_analyzer_agent_done",
            job_id=str(job.id),
            role=job.role,
            seniority=job.seniority,
            required_skills=len(job.required_skills),
            ats_keywords=len(job.ats_keywords),
        )
        return job

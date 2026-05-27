import uuid
from dataclasses import dataclass

from app.adapters.ai.workflows.resume_optimization.state import ResumeOptimizationState
from app.adapters.ai.workflows.resume_optimization.workflow import (
    get_resume_optimization_workflow,
)
from app.adapters.persistence.mappers.resume_mapper import (
    _deserialize_experience,
    _serialize_experience,
    _serialize_projects,
)
from app.application.ports.repositories.job_repository import JobRepository
from app.application.ports.repositories.resume_repository import ResumeRepository
from app.domain.entities.resume import Resume
from app.domain.enums.resume_strategy import ResumeStrategy
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, UnauthorizedError
from app.infrastructure.observability.structlog_setup import get_logger

logger = get_logger(__name__)


@dataclass
class OptimizeResumeInput:
    resume_id: uuid.UUID
    job_id: uuid.UUID
    user_id: uuid.UUID
    strategy: ResumeStrategy = ResumeStrategy.ATS_AGGRESSIVE
    label: str = ""


class OptimizeResumeUseCase:
    def __init__(
        self,
        resume_repo: ResumeRepository,
        job_repo: JobRepository,
    ) -> None:
        self._resume_repo = resume_repo
        self._job_repo = job_repo

    async def execute(self, data: OptimizeResumeInput) -> Resume:
        # Fetch and authorize
        resume = await self._resume_repo.get_by_id(data.resume_id)
        if not resume:
            raise EntityNotFoundError("Resume", str(data.resume_id))
        if resume.user_id != data.user_id:
            raise UnauthorizedError("Resume does not belong to this user")

        job = await self._job_repo.get_by_id(data.job_id)
        if not job:
            raise EntityNotFoundError("JobDescription", str(data.job_id))
        if job.user_id != data.user_id:
            raise UnauthorizedError("Job does not belong to this user")

        logger.info(
            "resume_optimization_start",
            resume_id=str(data.resume_id),
            strategy=data.strategy.value,
        )

        initial_state: ResumeOptimizationState = {
            "user_id": str(data.user_id),
            "resume_id": str(data.resume_id),
            "job_id": str(data.job_id),
            "strategy_mode": data.strategy.value,
            "original_resume": {
                "skills": resume.skills,
                "experience": _serialize_experience(resume.experience),
                "projects": _serialize_projects(resume.projects),
                "education": [],
                "certifications": [],
                "languages": resume.languages,
                "raw_text": resume.raw_text[:5000],
            },
            "job_data": {
                "title": job.title,
                "company": job.company,
                "role": job.role,
                "seniority": job.seniority,
                "domain": job.domain,
                "required_skills": job.required_skills,
                "preferred_skills": job.preferred_skills,
                "tools_and_technologies": job.tools_and_technologies,
                "ats_keywords": job.ats_keywords,
                "hidden_signals": job.hidden_signals,
            },
            "optimization_directives": {},
            "section_order": [],
            "tone": "professional",
            "emphasis_keywords": [],
            "deemphasize": [],
            "optimized_experience": [],
            "injected_skills": [],
            "final_skills": [],
            "optimized_resume": {},
            "pre_ats_score": 0.0,
            "post_ats_score": 0.0,
            "evaluation_passed": False,
            "iteration": 0,
            "max_iterations": 2,
            "critique_passed": False,
            "critique_feedback": "",
            "weak_points": [],
            "html_content": "",
            "pdf_url": "",
            "errors": [],
        }

        workflow = get_resume_optimization_workflow()
        final_state: ResumeOptimizationState = await workflow.ainvoke(initial_state)

        logger.info(
            "resume_optimization_complete",
            resume_id=str(data.resume_id),
            post_ats_score=final_state["post_ats_score"],
            critique_passed=final_state["critique_passed"],
        )

        # Build new optimized resume version
        optimized_data = final_state["optimized_resume"]
        optimized_experience = _deserialize_experience(
            optimized_data.get("experience", [])
        )

        # Carry over optimized bullets into impact statements description field
        for i, exp in enumerate(optimized_experience):
            raw_exp = optimized_data["experience"][i]
            bullets = raw_exp.get("optimized_bullets", [])
            if bullets:
                exp.description = "\n".join(f"• {b}" for b in bullets)

        label = data.label or f"{data.strategy.value} — {job.title}"
        optimized_resume = Resume(
            user_id=data.user_id,
            file_url=resume.file_url,
            file_name=resume.file_name,
            raw_text=resume.raw_text,
            skills=optimized_data.get("skills", resume.skills),
            experience=optimized_experience,
            projects=resume.projects,
            education=resume.education,
            certifications=resume.certifications,
            languages=resume.languages,
            version=resume.version + 1,
            label=label,
            strategy=data.strategy,
            parent_resume_id=resume.id,
            ats_score_snapshot=final_state["post_ats_score"],
        )

        return await self._resume_repo.create(optimized_resume)

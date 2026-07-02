import uuid
from dataclasses import dataclass

from app.adapters.ai.workflows.ats_scoring.state import ATSScoringState
from app.adapters.ai.workflows.ats_scoring.workflow import get_ats_scoring_workflow
from app.adapters.persistence.mappers.resume_mapper import (
    _serialize_experience,
    _serialize_projects,
)
from app.application.ports.repositories.ats_repository import ATSRepository
from app.application.ports.repositories.job_repository import JobRepository
from app.application.ports.repositories.resume_repository import ResumeRepository
from app.domain.entities.ats import ATSScore, ScoreDimension
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, UnauthorizedError
from app.infrastructure.observability.structlog_setup import get_logger

logger = get_logger(__name__)


@dataclass
class ScoreResumeInput:
    resume_id: uuid.UUID
    job_id: uuid.UUID
    user_id: uuid.UUID


class ScoreResumeUseCase:
    def __init__(
        self,
        ats_repo: ATSRepository,
        resume_repo: ResumeRepository,
        job_repo: JobRepository,
    ) -> None:
        self._ats_repo = ats_repo
        self._resume_repo = resume_repo
        self._job_repo = job_repo

    async def execute(self, data: ScoreResumeInput) -> ATSScore:
        # Fetch and authorize resume
        resume = await self._resume_repo.get_by_id(data.resume_id)
        if not resume:
            raise EntityNotFoundError("Resume", str(data.resume_id))
        if resume.user_id != data.user_id:
            raise UnauthorizedError("Resume does not belong to this user")

        # Fetch and authorize job
        job = await self._job_repo.get_by_id(data.job_id)
        if not job:
            raise EntityNotFoundError("JobDescription", str(data.job_id))
        if job.user_id != data.user_id:
            raise UnauthorizedError("Job does not belong to this user")

        logger.info(
            "ats_scoring_start",
            resume_id=str(data.resume_id),
            job_id=str(data.job_id),
        )

        # Build initial state
        initial_state: ATSScoringState = {
            "user_id": str(data.user_id),
            "resume_id": str(data.resume_id),
            "job_id": str(data.job_id),
            "resume_data": {
                "skills": resume.skills,
                "experience": _serialize_experience(resume.experience),
                "projects": _serialize_projects(resume.projects),
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
                "soft_skills": job.soft_skills,
            },
            # Initialize all score fields
            "keyword_score": 0.0,
            "keyword_matches": [],
            "keyword_gaps": [],
            "semantic_score": 0.0,
            "semantic_gaps": [],
            "technical_score": 0.0,
            "technical_feedback": "",
            "seniority_score": 0.0,
            "impact_score": 0.0,
            "ats_safety_score": 0.0,
            "readability_score": 0.0,
            "density_score": 0.0,
            "role_alignment_score": 0.0,
            "repetition_penalty": 0.0,
            "is_ats_safe": True,
            "safety_issues": [],
            "overall_score": 0.0,
            "dimension_breakdown": {},
            "recommendations": [],
            "missing_skills": [],
            "weak_sections": [],
            "recruiter_critique": "",
            "errors": [],
        }

        # Run workflow
        workflow = get_ats_scoring_workflow()
        final_state: ATSScoringState = await workflow.ainvoke(initial_state)

        logger.info(
            "ats_scoring_complete",
            resume_id=str(data.resume_id),
            overall_score=final_state["overall_score"],
        )

        # Build dimension entities from breakdown
        dimensions = [
            ScoreDimension(
                name=dim_name,
                score=dim_data["score"] / 100,
                weight=dim_data["weight"],
                feedback="",
            )
            for dim_name, dim_data in final_state["dimension_breakdown"].items()
        ]

        # Persist score
        ats_score = ATSScore(
            user_id=data.user_id,
            resume_id=data.resume_id,
            job_id=data.job_id,
            overall_score=final_state["overall_score"],
            dimensions=dimensions,
            missing_keywords=final_state.get("missing_skills", []),
            weak_sections=final_state.get("weak_sections", []),
            recommendations=final_state.get("recommendations", []),
            recruiter_critique=final_state.get("recruiter_critique", ""),
            is_ats_safe=final_state.get("is_ats_safe", True),
        )

        return await self._ats_repo.create(ats_score)

import uuid
from dataclasses import dataclass

from app.application.ports.repositories.resume_repository import ResumeRepository
from app.domain.entities.resume import Resume
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, UnauthorizedError


@dataclass
class ResumeComparison:
    base: Resume
    optimized: Resume
    added_skills: list[str]
    removed_skills: list[str]
    ats_score_delta: float | None
    experience_delta: int


class CompareResumeVersionsUseCase:
    def __init__(self, resume_repo: ResumeRepository) -> None:
        self._resume_repo = resume_repo

    async def execute(
        self, base_id: uuid.UUID, optimized_id: uuid.UUID, user_id: uuid.UUID
    ) -> ResumeComparison:
        base = await self._resume_repo.get_by_id(base_id)
        if not base:
            raise EntityNotFoundError("Resume", str(base_id))
        if base.user_id != user_id:
            raise UnauthorizedError("Resume does not belong to this user")

        optimized = await self._resume_repo.get_by_id(optimized_id)
        if not optimized:
            raise EntityNotFoundError("Resume", str(optimized_id))
        if optimized.user_id != user_id:
            raise UnauthorizedError("Resume does not belong to this user")

        base_skills = set(s.lower() for s in base.skills)
        opt_skills = set(s.lower() for s in optimized.skills)

        score_delta = None
        if base.ats_score_snapshot is not None and optimized.ats_score_snapshot is not None:
            score_delta = round(optimized.ats_score_snapshot - base.ats_score_snapshot, 1)

        return ResumeComparison(
            base=base,
            optimized=optimized,
            added_skills=list(opt_skills - base_skills),
            removed_skills=list(base_skills - opt_skills),
            ats_score_delta=score_delta,
            experience_delta=len(optimized.experience) - len(base.experience),
        )

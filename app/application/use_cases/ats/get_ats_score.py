import uuid

from app.application.ports.repositories.ats_repository import ATSRepository
from app.domain.entities.ats import ATSScore
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, UnauthorizedError


class GetATSScoreUseCase:
    def __init__(self, ats_repo: ATSRepository) -> None:
        self._ats_repo = ats_repo

    async def execute(self, score_id: uuid.UUID, user_id: uuid.UUID) -> ATSScore:
        score = await self._ats_repo.get_by_id(score_id)
        if not score:
            raise EntityNotFoundError("ATSScore", str(score_id))
        if score.user_id != user_id:
            raise UnauthorizedError("Score does not belong to this user")
        return score


class GetLatestATSScoreUseCase:
    def __init__(self, ats_repo: ATSRepository) -> None:
        self._ats_repo = ats_repo

    async def execute(
        self, resume_id: uuid.UUID, job_id: uuid.UUID, user_id: uuid.UUID
    ) -> ATSScore | None:
        return await self._ats_repo.get_by_resume_and_job(resume_id, job_id)

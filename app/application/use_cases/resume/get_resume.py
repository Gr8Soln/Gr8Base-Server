import uuid

from app.application.ports.repositories.resume_repository import ResumeRepository
from app.domain.entities.resume import Resume
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, UnauthorizedError


class GetResumeUseCase:
    def __init__(self, resume_repo: ResumeRepository) -> None:
        self._resume_repo = resume_repo

    async def execute(self, resume_id: uuid.UUID, user_id: uuid.UUID) -> Resume:
        resume = await self._resume_repo.get_by_id(resume_id)
        if not resume:
            raise EntityNotFoundError("Resume", str(resume_id))
        if resume.user_id != user_id:
            raise UnauthorizedError("Resume does not belong to this user")
        return resume

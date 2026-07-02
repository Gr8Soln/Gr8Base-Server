import uuid

from app.application.ports.repositories.resume_repository import ResumeRepository
from app.domain.entities.resume import Resume
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, UnauthorizedError


class RollbackResumeVersionUseCase:
    def __init__(self, resume_repo: ResumeRepository) -> None:
        self._resume_repo = resume_repo

    async def execute(self, resume_id: uuid.UUID, user_id: uuid.UUID) -> Resume:
        """
        Returns the parent resume of the given resume_id.
        The caller can then set this as their active resume.
        """
        resume = await self._resume_repo.get_by_id(resume_id)
        if not resume:
            raise EntityNotFoundError("Resume", str(resume_id))
        if resume.user_id != user_id:
            raise UnauthorizedError("Resume does not belong to this user")
        if not resume.parent_resume_id:
            raise EntityNotFoundError("Parent Resume", str(resume_id))

        parent = await self._resume_repo.get_by_id(resume.parent_resume_id)
        if not parent:
            raise EntityNotFoundError("Resume", str(resume.parent_resume_id))

        return parent

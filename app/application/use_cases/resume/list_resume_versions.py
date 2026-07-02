import uuid

from app.application.ports.repositories.resume_repository import ResumeRepository
from app.domain.entities.resume import Resume


class ListResumeVersionsUseCase:
    def __init__(self, resume_repo: ResumeRepository) -> None:
        self._resume_repo = resume_repo

    async def execute(self, user_id: uuid.UUID) -> list[Resume]:
        return await self._resume_repo.get_by_user_id(user_id)

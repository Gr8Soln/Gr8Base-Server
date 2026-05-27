import uuid

from app.application.ports.repositories.job_repository import JobRepository
from app.domain.entities.job import JobDescription
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, UnauthorizedError


class GetJobUseCase:
    def __init__(self, job_repo: JobRepository) -> None:
        self._job_repo = job_repo

    async def execute(self, job_id: uuid.UUID, user_id: uuid.UUID) -> JobDescription:
        job = await self._job_repo.get_by_id(job_id)
        if not job:
            raise EntityNotFoundError("JobDescription", str(job_id))
        if job.user_id != user_id:
            raise UnauthorizedError("Job does not belong to this user")
        return job

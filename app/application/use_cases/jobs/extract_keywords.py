import uuid

from app.application.ports.repositories.job_repository import JobRepository
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, UnauthorizedError


class ExtractKeywordsUseCase:
    def __init__(self, job_repo: JobRepository) -> None:
        self._job_repo = job_repo

    async def execute(self, job_id: uuid.UUID, user_id: uuid.UUID) -> list[str]:
        job = await self._job_repo.get_by_id(job_id)
        if not job:
            raise EntityNotFoundError("JobDescription", str(job_id))
        if job.user_id != user_id:
            raise UnauthorizedError("Job does not belong to this user")

        # Combine all keyword sources, deduplicated, preserving priority order
        seen: set[str] = set()
        keywords: list[str] = []
        for kw in [*job.ats_keywords, *job.required_skills, *job.tools_and_technologies]:
            normalized = kw.lower().strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                keywords.append(kw)
        return keywords

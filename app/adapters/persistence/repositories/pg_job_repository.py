import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.mappers.job_mapper import JobMapper
from app.adapters.persistence.models.job_model import JobModel
from app.application.ports.repositories.job_repository import JobRepository
from app.domain.entities.job import JobDescription
from app.domain.exceptions.domain_exceptions import EntityNotFoundError


class PgJobRepository(JobRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, job: JobDescription) -> JobDescription:
        model = JobMapper.to_model(job)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return JobMapper.to_entity(model)

    async def get_by_id(self, job_id: uuid.UUID) -> JobDescription | None:
        result = await self._session.execute(
            select(JobModel).where(JobModel.id == job_id)
        )
        model = result.scalar_one_or_none()
        return JobMapper.to_entity(model) if model else None

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[JobDescription]:
        result = await self._session.execute(
            select(JobModel)
            .where(JobModel.user_id == user_id)
            .order_by(JobModel.created_at.desc())
        )
        return [JobMapper.to_entity(m) for m in result.scalars().all()]

    async def update(self, job: JobDescription) -> JobDescription:
        result = await self._session.execute(
            select(JobModel).where(JobModel.id == job.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise EntityNotFoundError("JobDescription", str(job.id))

        model.raw_text = job.raw_text
        model.title = job.title
        model.company = job.company
        model.company_url = job.company_url
        model.location = job.location
        model.work_type = job.work_type
        model.role = job.role
        model.seniority = job.seniority
        model.domain = job.domain
        model.required_skills = job.required_skills
        model.preferred_skills = job.preferred_skills
        model.soft_skills = job.soft_skills
        model.tools_and_technologies = job.tools_and_technologies
        model.ats_keywords = job.ats_keywords
        model.hidden_signals = job.hidden_signals
        model.salary_min = job.salary_min
        model.salary_max = job.salary_max
        await self._session.flush()
        await self._session.refresh(model)
        return JobMapper.to_entity(model)

    async def delete(self, job_id: uuid.UUID) -> None:
        result = await self._session.execute(
            select(JobModel).where(JobModel.id == job_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def search_similar(
        self, embedding: list[float], user_id: uuid.UUID, limit: int = 5
    ) -> list[JobDescription]:
        # pgvector similarity — implemented in Phase 5 vector section
        return []

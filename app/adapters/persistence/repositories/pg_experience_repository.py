import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.mappers.experience_mapper import ExperienceMapper
from app.adapters.persistence.models.experience_model import ExperienceModel
from app.application.ports.repositories.experience_repository import ExperienceRepository
from app.domain.entities.experience import WorkExperience
from app.domain.exceptions.domain_exceptions import EntityNotFoundError


class PgExperienceRepository(ExperienceRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, experience: WorkExperience) -> WorkExperience:
        model = ExperienceMapper.to_model(experience)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return ExperienceMapper.to_entity(model)

    async def get_by_id(self, experience_id: uuid.UUID) -> WorkExperience | None:
        result = await self._session.execute(
            select(ExperienceModel).where(ExperienceModel.id == experience_id)
        )
        model = result.scalar_one_or_none()
        return ExperienceMapper.to_entity(model) if model else None

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[WorkExperience]:
        result = await self._session.execute(
            select(ExperienceModel)
            .where(ExperienceModel.user_id == user_id)
            .order_by(ExperienceModel.start_date.desc())
        )
        return [ExperienceMapper.to_entity(m) for m in result.scalars().all()]

    async def update(self, experience: WorkExperience) -> WorkExperience:
        result = await self._session.execute(
            select(ExperienceModel).where(ExperienceModel.id == experience.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise EntityNotFoundError("WorkExperience", str(experience.id))
        updated = ExperienceMapper.to_model(experience)
        for key in (
            "company",
            "role",
            "start_date",
            "end_date",
            "is_current",
            "location",
            "description",
            "employment_type",
            "industry",
            "company_website",
            "responsibilities",
            "achievements",
            "technologies",
            "impact_statements",
            "related_projects",
            "ai_summary",
            "embedding",
            "enrichment_data",
        ):
            setattr(model, key, getattr(updated, key))
        await self._session.flush()
        await self._session.refresh(model)
        return ExperienceMapper.to_entity(model)

    async def delete(self, experience_id: uuid.UUID) -> None:
        result = await self._session.execute(
            select(ExperienceModel).where(ExperienceModel.id == experience_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def bulk_create(self, experiences: list[WorkExperience]) -> list[WorkExperience]:
        models = [ExperienceMapper.to_model(e) for e in experiences]
        self._session.add_all(models)
        await self._session.flush()
        return [ExperienceMapper.to_entity(m) for m in models]

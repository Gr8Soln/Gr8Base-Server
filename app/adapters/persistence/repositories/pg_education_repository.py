import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.mappers.education_mapper import EducationMapper
from app.adapters.persistence.models.education_model import EducationModel
from app.application.ports.repositories.education_repository import EducationRepository
from app.domain.entities.education import Education
from app.domain.exceptions.domain_exceptions import EntityNotFoundError


class PgEducationRepository(EducationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, education: Education) -> Education:
        model = EducationMapper.to_model(education)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return EducationMapper.to_entity(model)

    async def get_by_id(self, education_id: uuid.UUID) -> Education | None:
        result = await self._session.execute(
            select(EducationModel).where(EducationModel.id == education_id)
        )
        model = result.scalar_one_or_none()
        return EducationMapper.to_entity(model) if model else None

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[Education]:
        result = await self._session.execute(
            select(EducationModel).where(EducationModel.user_id == user_id)
        )
        return [EducationMapper.to_entity(m) for m in result.scalars().all()]

    async def update(self, education: Education) -> Education:
        result = await self._session.execute(
            select(EducationModel).where(EducationModel.id == education.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise EntityNotFoundError("Education", str(education.id))
        updated = EducationMapper.to_model(education)
        for key in (
            "institution",
            "degree",
            "field_of_study",
            "start_year",
            "end_year",
            "gpa",
            "honors",
            "activities",
        ):
            setattr(model, key, getattr(updated, key))
        await self._session.flush()
        await self._session.refresh(model)
        return EducationMapper.to_entity(model)

    async def delete(self, education_id: uuid.UUID) -> None:
        result = await self._session.execute(
            select(EducationModel).where(EducationModel.id == education_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def bulk_create(self, entries: list[Education]) -> list[Education]:
        models = [EducationMapper.to_model(e) for e in entries]
        self._session.add_all(models)
        await self._session.flush()
        return [EducationMapper.to_entity(m) for m in models]

    async def delete_all_for_user(self, user_id: uuid.UUID) -> None:
        await self._session.execute(delete(EducationModel).where(EducationModel.user_id == user_id))
        await self._session.flush()

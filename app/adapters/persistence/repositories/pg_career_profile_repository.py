import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.mappers.career_profile_mapper import CareerProfileMapper
from app.adapters.persistence.models.career_profile_model import CareerProfileModel
from app.application.ports.repositories.career_profile_repository import CareerProfileRepository
from app.domain.entities.career_profile import CareerProfile
from app.domain.exceptions.domain_exceptions import EntityNotFoundError


class PgCareerProfileRepository(CareerProfileRepository):
    """Repository for the canonical CareerProfile entity."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, profile: CareerProfile) -> CareerProfile:
        model = CareerProfileMapper.to_model(profile)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return CareerProfileMapper.to_entity(model)

    async def get_by_user_id(self, user_id: uuid.UUID) -> CareerProfile | None:
        result = await self._session.execute(
            select(CareerProfileModel).where(CareerProfileModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        return CareerProfileMapper.to_entity(model) if model else None

    async def update(self, profile: CareerProfile) -> CareerProfile:
        result = await self._session.execute(
            select(CareerProfileModel).where(CareerProfileModel.id == profile.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise EntityNotFoundError("CareerProfile", str(profile.id))
        updated = CareerProfileMapper.to_model(profile)
        for key in (
            "full_name",
            "email",
            "headline",
            "summary",
            "location",
            "phone",
            "address",
            "linkedin_url",
            "github_url",
            "portfolio_url",
            "website",
            "years_of_experience",
            "target_roles",
            "target_industries",
            "target_salary_min",
            "target_salary_max",
            "preferred_work_type",
            "writing_tone",
            "summary_embedding",
        ):
            setattr(model, key, getattr(updated, key))
        await self._session.flush()
        await self._session.refresh(model)
        return CareerProfileMapper.to_entity(model)

    async def delete(self, user_id: uuid.UUID) -> None:
        result = await self._session.execute(
            select(CareerProfileModel).where(CareerProfileModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()

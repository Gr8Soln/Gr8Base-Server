import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.mappers.technology_mapper import TechnologyMapper
from app.adapters.persistence.models.technology_model import TechnologyModel
from app.application.ports.repositories.technology_repository import TechnologyRepository
from app.domain.entities.technology import Technology
from app.domain.exceptions.domain_exceptions import EntityNotFoundError


class PgTechnologyRepository(TechnologyRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, tech: Technology) -> Technology:
        model = TechnologyMapper.to_model(tech)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return TechnologyMapper.to_entity(model)

    async def get_by_id(self, tech_id: uuid.UUID) -> Technology | None:
        result = await self._session.execute(
            select(TechnologyModel).where(TechnologyModel.id == tech_id))
        model = result.scalar_one_or_none()
        return TechnologyMapper.to_entity(model) if model else None

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[Technology]:
        result = await self._session.execute(
            select(TechnologyModel).where(TechnologyModel.user_id == user_id))
        return [TechnologyMapper.to_entity(m) for m in result.scalars().all()]

    async def update(self, tech: Technology) -> Technology:
        result = await self._session.execute(
            select(TechnologyModel).where(TechnologyModel.id == tech.id))
        model = result.scalar_one_or_none()
        if not model:
            raise EntityNotFoundError("Technology", str(tech.id))
        updated = TechnologyMapper.to_model(tech)
        for key in ("name", "category", "proficiency"):
            setattr(model, key, getattr(updated, key))
        await self._session.flush()
        await self._session.refresh(model)
        return TechnologyMapper.to_entity(model)

    async def delete(self, tech_id: uuid.UUID) -> None:
        result = await self._session.execute(
            select(TechnologyModel).where(TechnologyModel.id == tech_id))
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def bulk_create(self, techs: list[Technology]) -> list[Technology]:
        models = [TechnologyMapper.to_model(t) for t in techs]
        self._session.add_all(models)
        await self._session.flush()
        return [TechnologyMapper.to_entity(m) for m in models]

    async def delete_all_for_user(self, user_id: uuid.UUID) -> None:
        await self._session.execute(
            delete(TechnologyModel).where(TechnologyModel.user_id == user_id))
        await self._session.flush()

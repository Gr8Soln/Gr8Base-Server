import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.mappers.award_mapper import AwardMapper
from app.adapters.persistence.models.award_model import AwardModel
from app.application.ports.repositories.award_repository import AwardRepository
from app.domain.entities.award import Award
from app.domain.exceptions.domain_exceptions import EntityNotFoundError


class PgAwardRepository(AwardRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, award: Award) -> Award:
        model = AwardMapper.to_model(award)
        self._session.add(model)
        await self._session.flush(); await self._session.refresh(model)
        return AwardMapper.to_entity(model)

    async def get_by_id(self, award_id: uuid.UUID) -> Award | None:
        result = await self._session.execute(select(AwardModel).where(AwardModel.id == award_id))
        model = result.scalar_one_or_none()
        return AwardMapper.to_entity(model) if model else None

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[Award]:
        result = await self._session.execute(
            select(AwardModel).where(AwardModel.user_id == user_id))
        return [AwardMapper.to_entity(m) for m in result.scalars().all()]

    async def update(self, award: Award) -> Award:
        result = await self._session.execute(select(AwardModel).where(AwardModel.id == award.id))
        model = result.scalar_one_or_none()
        if not model: raise EntityNotFoundError("Award", str(award.id))
        updated = AwardMapper.to_model(award)
        for key in ("name", "issuer", "date", "description"):
            setattr(model, key, getattr(updated, key))
        await self._session.flush(); await self._session.refresh(model)
        return AwardMapper.to_entity(model)

    async def delete(self, award_id: uuid.UUID) -> None:
        result = await self._session.execute(select(AwardModel).where(AwardModel.id == award_id))
        model = result.scalar_one_or_none()
        if model: await self._session.delete(model); await self._session.flush()

    async def bulk_create(self, awards: list[Award]) -> list[Award]:
        models = [AwardMapper.to_model(a) for a in awards]
        self._session.add_all(models); await self._session.flush()
        return [AwardMapper.to_entity(m) for m in models]

    async def delete_all_for_user(self, user_id: uuid.UUID) -> None:
        await self._session.execute(delete(AwardModel).where(AwardModel.user_id == user_id))
        await self._session.flush()

import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.mappers.skill_mapper import SkillMapper
from app.adapters.persistence.models.skill_model import SkillModel
from app.application.ports.repositories.skill_repository import SkillRepository
from app.domain.entities.skill import Skill
from app.domain.exceptions.domain_exceptions import EntityNotFoundError


class PgSkillRepository(SkillRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, skill: Skill) -> Skill:
        model = SkillMapper.to_model(skill)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return SkillMapper.to_entity(model)

    async def get_by_id(self, skill_id: uuid.UUID) -> Skill | None:
        result = await self._session.execute(select(SkillModel).where(SkillModel.id == skill_id))
        model = result.scalar_one_or_none()
        return SkillMapper.to_entity(model) if model else None

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[Skill]:
        result = await self._session.execute(
            select(SkillModel).where(SkillModel.user_id == user_id)
        )
        return [SkillMapper.to_entity(m) for m in result.scalars().all()]

    async def update(self, skill: Skill) -> Skill:
        result = await self._session.execute(select(SkillModel).where(SkillModel.id == skill.id))
        model = result.scalar_one_or_none()
        if not model:
            raise EntityNotFoundError("Skill", str(skill.id))
        updated = SkillMapper.to_model(skill)
        for key in ("name", "category", "proficiency", "years_of_experience"):
            setattr(model, key, getattr(updated, key))
        await self._session.flush()
        await self._session.refresh(model)
        return SkillMapper.to_entity(model)

    async def delete(self, skill_id: uuid.UUID) -> None:
        result = await self._session.execute(select(SkillModel).where(SkillModel.id == skill_id))
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def bulk_create(self, skills: list[Skill]) -> list[Skill]:
        models = [SkillMapper.to_model(s) for s in skills]
        self._session.add_all(models)
        await self._session.flush()
        return [SkillMapper.to_entity(m) for m in models]

    async def delete_all_for_user(self, user_id: uuid.UUID) -> None:
        await self._session.execute(delete(SkillModel).where(SkillModel.user_id == user_id))
        await self._session.flush()

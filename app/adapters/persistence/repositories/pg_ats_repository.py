import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.mappers.ats_mapper import ATSScoreMapper
from app.adapters.persistence.models.ats_model import ATSScoreModel
from app.application.ports.repositories.ats_repository import ATSRepository
from app.domain.entities.ats import ATSScore


class PgATSRepository(ATSRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, score: ATSScore) -> ATSScore:
        model = ATSScoreMapper.to_model(score)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return ATSScoreMapper.to_entity(model)

    async def get_by_id(self, score_id: uuid.UUID) -> ATSScore | None:
        result = await self._session.execute(
            select(ATSScoreModel).where(ATSScoreModel.id == score_id)
        )
        model = result.scalar_one_or_none()
        return ATSScoreMapper.to_entity(model) if model else None

    async def get_by_resume_and_job(
        self, resume_id: uuid.UUID, job_id: uuid.UUID
    ) -> ATSScore | None:
        result = await self._session.execute(
            select(ATSScoreModel)
            .where(
                ATSScoreModel.resume_id == resume_id,
                ATSScoreModel.job_id == job_id,
            )
            .order_by(ATSScoreModel.created_at.desc())
        )
        model = result.scalar_one_or_none()
        return ATSScoreMapper.to_entity(model) if model else None

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[ATSScore]:
        result = await self._session.execute(
            select(ATSScoreModel)
            .where(ATSScoreModel.user_id == user_id)
            .order_by(ATSScoreModel.created_at.desc())
        )
        return [ATSScoreMapper.to_entity(m) for m in result.scalars().all()]

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.mappers.resume_mapper import ResumeMapper
from app.adapters.persistence.models.resume_model import ResumeModel
from app.application.ports.repositories.resume_repository import ResumeRepository
from app.domain.entities.resume import Resume
from app.domain.exceptions.domain_exceptions import EntityNotFoundError


class PgResumeRepository(ResumeRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, resume: Resume) -> Resume:
        model = ResumeMapper.to_model(resume)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return ResumeMapper.to_entity(model)

    async def get_by_id(self, resume_id: uuid.UUID) -> Resume | None:
        result = await self._session.execute(
            select(ResumeModel).where(ResumeModel.id == resume_id)
        )
        model = result.scalar_one_or_none()
        return ResumeMapper.to_entity(model) if model else None

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[Resume]:
        result = await self._session.execute(
            select(ResumeModel)
            .where(ResumeModel.user_id == user_id)
            .order_by(ResumeModel.created_at.desc())
        )
        return [ResumeMapper.to_entity(m) for m in result.scalars().all()]

    async def get_versions(self, parent_id: uuid.UUID) -> list[Resume]:
        result = await self._session.execute(
            select(ResumeModel)
            .where(ResumeModel.parent_resume_id == parent_id)
            .order_by(ResumeModel.version.asc())
        )
        return [ResumeMapper.to_entity(m) for m in result.scalars().all()]

    async def update(self, resume: Resume) -> Resume:
        result = await self._session.execute(
            select(ResumeModel).where(ResumeModel.id == resume.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise EntityNotFoundError("Resume", str(resume.id))

        updated = ResumeMapper.to_model(resume)
        model.raw_text = updated.raw_text
        model.skills = updated.skills
        model.experience = updated.experience
        model.projects = updated.projects
        model.education = updated.education
        model.certifications = updated.certifications
        model.languages = updated.languages
        model.label = updated.label
        model.strategy = updated.strategy
        model.ats_score_snapshot = updated.ats_score_snapshot

        await self._session.flush()
        await self._session.refresh(model)
        return ResumeMapper.to_entity(model)

    async def delete(self, resume_id: uuid.UUID) -> None:
        result = await self._session.execute(
            select(ResumeModel).where(ResumeModel.id == resume_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def search_similar(
        self, embedding: list[float], user_id: uuid.UUID, limit: int = 5
    ) -> list[Resume]:
        # pgvector similarity search — implemented in Phase 5
        return []

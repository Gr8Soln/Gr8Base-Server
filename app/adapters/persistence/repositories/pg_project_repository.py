import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.mappers.project_mapper import ProjectMapper
from app.adapters.persistence.models.project_model import ProjectModel
from app.application.ports.repositories.project_repository import ProjectRepository
from app.domain.entities.project import Project
from app.domain.exceptions.domain_exceptions import EntityNotFoundError


class PgProjectRepository(ProjectRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, project: Project) -> Project:
        model = ProjectMapper.to_model(project)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return ProjectMapper.to_entity(model)

    async def get_by_id(self, project_id: uuid.UUID) -> Project | None:
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.id == project_id)
        )
        model = result.scalar_one_or_none()
        return ProjectMapper.to_entity(model) if model else None

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[Project]:
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.user_id == user_id)
            .order_by(ProjectModel.created_at.desc())
        )
        return [ProjectMapper.to_entity(m) for m in result.scalars().all()]

    async def update(self, project: Project) -> Project:
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.id == project.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise EntityNotFoundError("Project", str(project.id))
        updated = ProjectMapper.to_model(project)
        for key in ("name", "description", "role", "technologies",
                     "responsibilities", "repository", "demo_url", "url",
                     "duration", "impact", "ai_summary", "embedding"):
            setattr(model, key, getattr(updated, key))
        await self._session.flush()
        await self._session.refresh(model)
        return ProjectMapper.to_entity(model)

    async def delete(self, project_id: uuid.UUID) -> None:
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.id == project_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def bulk_create(self, projects: list[Project]) -> list[Project]:
        models = [ProjectMapper.to_model(p) for p in projects]
        self._session.add_all(models)
        await self._session.flush()
        return [ProjectMapper.to_entity(m) for m in models]

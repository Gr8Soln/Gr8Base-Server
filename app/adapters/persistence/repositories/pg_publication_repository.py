import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.mappers.publication_mapper import PublicationMapper
from app.adapters.persistence.models.publication_model import PublicationModel
from app.application.ports.repositories.publication_repository import PublicationRepository
from app.domain.entities.publication import Publication
from app.domain.exceptions.domain_exceptions import EntityNotFoundError


class PgPublicationRepository(PublicationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, pub: Publication) -> Publication:
        model = PublicationMapper.to_model(pub)
        self._session.add(model); await self._session.flush(); await self._session.refresh(model)
        return PublicationMapper.to_entity(model)

    async def get_by_id(self, pub_id: uuid.UUID) -> Publication | None:
        result = await self._session.execute(
            select(PublicationModel).where(PublicationModel.id == pub_id))
        model = result.scalar_one_or_none()
        return PublicationMapper.to_entity(model) if model else None

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[Publication]:
        result = await self._session.execute(
            select(PublicationModel).where(PublicationModel.user_id == user_id))
        return [PublicationMapper.to_entity(m) for m in result.scalars().all()]

    async def update(self, pub: Publication) -> Publication:
        result = await self._session.execute(
            select(PublicationModel).where(PublicationModel.id == pub.id))
        model = result.scalar_one_or_none()
        if not model: raise EntityNotFoundError("Publication", str(pub.id))
        updated = PublicationMapper.to_model(pub)
        for key in ("title", "publisher", "date", "url", "description"):
            setattr(model, key, getattr(updated, key))
        await self._session.flush(); await self._session.refresh(model)
        return PublicationMapper.to_entity(model)

    async def delete(self, pub_id: uuid.UUID) -> None:
        result = await self._session.execute(
            select(PublicationModel).where(PublicationModel.id == pub_id))
        model = result.scalar_one_or_none()
        if model: await self._session.delete(model); await self._session.flush()

    async def bulk_create(self, pubs: list[Publication]) -> list[Publication]:
        models = [PublicationMapper.to_model(p) for p in pubs]
        self._session.add_all(models); await self._session.flush()
        return [PublicationMapper.to_entity(m) for m in models]

    async def delete_all_for_user(self, user_id: uuid.UUID) -> None:
        await self._session.execute(
            delete(PublicationModel).where(PublicationModel.user_id == user_id))
        await self._session.flush()

import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.mappers.language_mapper import LanguageMapper
from app.adapters.persistence.models.language_model import LanguageModel
from app.application.ports.repositories.language_repository import LanguageRepository
from app.domain.entities.language import Language
from app.domain.exceptions.domain_exceptions import EntityNotFoundError


class PgLanguageRepository(LanguageRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, language: Language) -> Language:
        model = LanguageMapper.to_model(language)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return LanguageMapper.to_entity(model)

    async def get_by_id(self, lang_id: uuid.UUID) -> Language | None:
        result = await self._session.execute(
            select(LanguageModel).where(LanguageModel.id == lang_id)
        )
        model = result.scalar_one_or_none()

        return LanguageMapper.to_entity(model) if model else None

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[Language]:
        result = await self._session.execute(
            select(LanguageModel).where(LanguageModel.user_id == user_id)
        )

        return [LanguageMapper.to_entity(m) for m in result.scalars().all()]

    async def update(self, language: Language) -> Language:
        result = await self._session.execute(
            select(LanguageModel).where(LanguageModel.id == language.id)
        )
        model = result.scalar_one_or_none()

        if not model:
            raise EntityNotFoundError("Language", str(language.id))

        updated = LanguageMapper.to_model(language)
        for key in ("name", "proficiency"):
            setattr(model, key, getattr(updated, key))
        await self._session.flush()
        await self._session.refresh(model)

        return LanguageMapper.to_entity(model)

    async def delete(self, lang_id: uuid.UUID) -> None:
        result = await self._session.execute(
            select(LanguageModel).where(LanguageModel.id == lang_id)
        )
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def bulk_create(self, languages: list[Language]) -> list[Language]:
        models = [LanguageMapper.to_model(l) for l in languages]
        self._session.add_all(models)
        await self._session.flush()

        return [LanguageMapper.to_entity(m) for m in models]

    async def delete_all_for_user(self, user_id: uuid.UUID) -> None:
        await self._session.execute(delete(LanguageModel).where(LanguageModel.user_id == user_id))

        await self._session.flush()

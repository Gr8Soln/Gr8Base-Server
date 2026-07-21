import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.mappers.certification_mapper import CertificationMapper
from app.adapters.persistence.models.certification_model import CertificationModel
from app.application.ports.repositories.certification_repository import CertificationRepository
from app.domain.entities.certification import Certification
from app.domain.exceptions.domain_exceptions import EntityNotFoundError


class PgCertificationRepository(CertificationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, cert: Certification) -> Certification:
        model = CertificationMapper.to_model(cert)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return CertificationMapper.to_entity(model)

    async def get_by_id(self, cert_id: uuid.UUID) -> Certification | None:
        result = await self._session.execute(
            select(CertificationModel).where(CertificationModel.id == cert_id)
        )
        model = result.scalar_one_or_none()
        return CertificationMapper.to_entity(model) if model else None

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[Certification]:
        result = await self._session.execute(
            select(CertificationModel).where(CertificationModel.user_id == user_id)
        )
        return [CertificationMapper.to_entity(m) for m in result.scalars().all()]

    async def update(self, cert: Certification) -> Certification:
        result = await self._session.execute(
            select(CertificationModel).where(CertificationModel.id == cert.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise EntityNotFoundError("Certification", str(cert.id))
        updated = CertificationMapper.to_model(cert)
        for key in (
            "name",
            "issuer",
            "issue_date",
            "expiry_date",
            "credential_url",
            "credential_id",
        ):
            setattr(model, key, getattr(updated, key))
        await self._session.flush()
        await self._session.refresh(model)
        return CertificationMapper.to_entity(model)

    async def delete(self, cert_id: uuid.UUID) -> None:
        result = await self._session.execute(
            select(CertificationModel).where(CertificationModel.id == cert_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def bulk_create(self, certs: list[Certification]) -> list[Certification]:
        models = [CertificationMapper.to_model(c) for c in certs]
        self._session.add_all(models)
        await self._session.flush()
        return [CertificationMapper.to_entity(m) for m in models]

    async def delete_all_for_user(self, user_id: uuid.UUID) -> None:
        await self._session.execute(
            delete(CertificationModel).where(CertificationModel.user_id == user_id)
        )
        await self._session.flush()

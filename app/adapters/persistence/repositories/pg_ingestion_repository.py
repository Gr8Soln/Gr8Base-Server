import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.mappers.ingestion_mapper import IngestionMapper
from app.adapters.persistence.models.ingestion_model import IngestionWorkflowModel
from app.application.ports.repositories.ingestion_repository import (
    IngestionRepository,
    IngestionWorkflow,
)
from app.domain.enums.ingestion_status import IngestionStatus
from app.domain.exceptions.domain_exceptions import EntityNotFoundError


class PgIngestionRepository(IngestionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, workflow: IngestionWorkflow) -> IngestionWorkflow:
        model = IngestionMapper.to_model(workflow)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return IngestionMapper.to_entity(model)

    async def get_by_id(self, workflow_id: uuid.UUID) -> IngestionWorkflow | None:
        result = await self._session.execute(
            select(IngestionWorkflowModel).where(IngestionWorkflowModel.id == workflow_id)
        )
        model = result.scalar_one_or_none()
        return IngestionMapper.to_entity(model) if model else None

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[IngestionWorkflow]:
        result = await self._session.execute(
            select(IngestionWorkflowModel)
            .where(IngestionWorkflowModel.user_id == user_id)
            .order_by(IngestionWorkflowModel.created_at.desc())
        )
        return [IngestionMapper.to_entity(m) for m in result.scalars().all()]

    async def update_status(
        self, workflow_id: uuid.UUID, status: IngestionStatus, error_message: str = ""
    ) -> IngestionWorkflow:
        result = await self._session.execute(
            select(IngestionWorkflowModel).where(IngestionWorkflowModel.id == workflow_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise EntityNotFoundError("IngestionWorkflow", str(workflow_id))
        model.status = status.value
        if error_message:
            model.error_message = error_message
        await self._session.flush()
        await self._session.refresh(model)
        return IngestionMapper.to_entity(model)

    async def append_event(self, workflow_id: uuid.UUID, event_type: str, event_data: dict) -> None:
        result = await self._session.execute(
            select(IngestionWorkflowModel).where(IngestionWorkflowModel.id == workflow_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return
        events = list(model.events or [])
        events.append({"type": event_type, "data": event_data})
        model.events = events
        await self._session.flush()

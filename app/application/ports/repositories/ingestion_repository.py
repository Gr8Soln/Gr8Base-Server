import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.enums.ingestion_status import IngestionStatus


@dataclass
class IngestionWorkflow:
    id: uuid.UUID
    user_id: uuid.UUID
    status: IngestionStatus = IngestionStatus.PENDING
    source_file_key: str = ""
    source_file_name: str = ""
    source_file_url: str = ""
    error_message: str = ""
    events: list[dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class IngestionRepository(ABC):
    @abstractmethod
    async def create(self, workflow: IngestionWorkflow) -> IngestionWorkflow: ...
    @abstractmethod
    async def get_by_id(self, workflow_id: uuid.UUID) -> IngestionWorkflow | None: ...
    @abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID) -> list[IngestionWorkflow]: ...
    @abstractmethod
    async def update_status(
        self, workflow_id: uuid.UUID, status: IngestionStatus, error_message: str = ""
    ) -> IngestionWorkflow: ...
    @abstractmethod
    async def append_event(
        self, workflow_id: uuid.UUID, event_type: str, event_data: dict
    ) -> None: ...

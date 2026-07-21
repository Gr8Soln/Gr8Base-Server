import uuid
from dataclasses import dataclass

from app.adapters.ingestion.ingestion_router import extract_text
from app.application.ports.repositories.ingestion_repository import (
    IngestionRepository,
    IngestionWorkflow,
)
from app.application.ports.storage.file_storage_port import FileStoragePort
from app.domain.enums.ingestion_status import IngestionStatus


@dataclass
class IngestResumeInput:
    user_id: uuid.UUID
    file_bytes: bytes
    filename: str
    content_type: str


@dataclass
class IngestResumeOutput:
    workflow_id: uuid.UUID
    status: str
    file_url: str


class IngestResumeUseCase:
    """Orchestrates the full resume ingestion pipeline.

    1. Store original document in R2
    2. Extract raw text
    3. Create ingestion workflow
    4. Kick off async pipeline (parse → enrich → embed → persist)
    """

    def __init__(
        self,
        storage: FileStoragePort,
        ingestion_repo: IngestionRepository,
    ) -> None:
        self._storage = storage
        self._ingestion_repo = ingestion_repo

    async def execute(self, data: IngestResumeInput) -> IngestResumeOutput:
        # Validate file
        raw_text = extract_text(
            file_bytes=data.file_bytes,
            content_type=data.content_type,
            filename=data.filename,
        )

        # Store original file
        storage_key = f"career/{data.user_id}/{uuid.uuid4()}_{data.filename}"
        file_url = await self._storage.upload(
            file_bytes=data.file_bytes,
            key=storage_key,
            content_type=data.content_type,
        )

        # Create ingestion workflow record
        workflow = await self._ingestion_repo.create(
            IngestionWorkflow(
                id=uuid.uuid4(),
                user_id=data.user_id,
                status=IngestionStatus.PENDING,
                source_file_key=storage_key,
                source_file_name=data.filename,
                source_file_url=file_url,
            )
        )

        return IngestResumeOutput(
            workflow_id=workflow.id,
            status=workflow.status.value,
            file_url=file_url,
        )

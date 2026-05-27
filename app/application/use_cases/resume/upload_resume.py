import uuid
from dataclasses import dataclass

from app.application.ports.repositories.resume_repository import ResumeRepository
from app.application.ports.storage.file_storage_port import FileStoragePort
from app.domain.entities.resume import Resume


@dataclass
class UploadResumeInput:
    user_id: uuid.UUID
    file_bytes: bytes
    filename: str
    content_type: str


@dataclass
class UploadResumeOutput:
    resume: Resume
    storage_key: str


class UploadResumeUseCase:
    def __init__(
        self,
        resume_repo: ResumeRepository,
        storage: FileStoragePort,
    ) -> None:
        self._resume_repo = resume_repo
        self._storage = storage

    async def execute(self, data: UploadResumeInput) -> UploadResumeOutput:
        storage_key = f"resumes/{data.user_id}/{uuid.uuid4()}_{data.filename}"
        file_url = await self._storage.upload(
            file_bytes=data.file_bytes,
            key=storage_key,
            content_type=data.content_type,
        )

        resume = Resume(
            user_id=data.user_id,
            file_url=file_url,
            file_name=data.filename,
            raw_text="",  # populated after parsing
        )
        resume = await self._resume_repo.create(resume)

        return UploadResumeOutput(resume=resume, storage_key=storage_key)

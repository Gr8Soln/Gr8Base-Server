import uuid
from abc import ABC, abstractmethod

from app.domain.entities.job import JobDescription


class JobRepository(ABC):
    @abstractmethod
    async def create(self, job: JobDescription) -> JobDescription: ...

    @abstractmethod
    async def get_by_id(self, job_id: uuid.UUID) -> JobDescription | None: ...

    @abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID) -> list[JobDescription]: ...

    @abstractmethod
    async def update(self, job: JobDescription) -> JobDescription: ...

    @abstractmethod
    async def delete(self, job_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def search_similar(
        self, embedding: list[float], user_id: uuid.UUID, limit: int = 5
    ) -> list[JobDescription]: ...

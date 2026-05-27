import uuid
from abc import ABC, abstractmethod

from app.domain.entities.resume import Resume


class ResumeRepository(ABC):
    @abstractmethod
    async def create(self, resume: Resume) -> Resume: ...

    @abstractmethod
    async def get_by_id(self, resume_id: uuid.UUID) -> Resume | None: ...

    @abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID) -> list[Resume]: ...

    @abstractmethod
    async def get_versions(self, parent_id: uuid.UUID) -> list[Resume]: ...

    @abstractmethod
    async def update(self, resume: Resume) -> Resume: ...

    @abstractmethod
    async def delete(self, resume_id: uuid.UUID) -> None: ...

    @abstractmethod
    async def search_similar(
        self, embedding: list[float], user_id: uuid.UUID, limit: int = 5
    ) -> list[Resume]: ...

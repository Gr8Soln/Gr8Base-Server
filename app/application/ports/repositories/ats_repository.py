import uuid
from abc import ABC, abstractmethod

from app.domain.entities.ats import ATSScore


class ATSRepository(ABC):
    @abstractmethod
    async def create(self, score: ATSScore) -> ATSScore: ...

    @abstractmethod
    async def get_by_id(self, score_id: uuid.UUID) -> ATSScore | None: ...

    @abstractmethod
    async def get_by_resume_and_job(
        self, resume_id: uuid.UUID, job_id: uuid.UUID
    ) -> ATSScore | None: ...

    @abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID) -> list[ATSScore]: ...

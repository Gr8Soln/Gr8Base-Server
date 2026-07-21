import uuid
from abc import ABC, abstractmethod

from app.domain.entities.career_profile import CareerProfile


class CareerProfileRepository(ABC):
    """Repository for the canonical CareerProfile entity."""

    @abstractmethod
    async def create(self, profile: CareerProfile) -> CareerProfile: ...
    @abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID) -> CareerProfile | None: ...
    @abstractmethod
    async def update(self, profile: CareerProfile) -> CareerProfile: ...
    @abstractmethod
    async def delete(self, user_id: uuid.UUID) -> None: ...

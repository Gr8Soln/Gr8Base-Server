import uuid
from abc import ABC, abstractmethod

from app.domain.entities.user import CareerProfile, User


class UserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User: ...

    @abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def update(self, user: User) -> User: ...

    @abstractmethod
    async def delete(self, user_id: uuid.UUID) -> None: ...


class CareerProfileRepository(ABC):
    @abstractmethod
    async def create(self, profile: CareerProfile) -> CareerProfile: ...

    @abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID) -> CareerProfile | None: ...

    @abstractmethod
    async def update(self, profile: CareerProfile) -> CareerProfile: ...

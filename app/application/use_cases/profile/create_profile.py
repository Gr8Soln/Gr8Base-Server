import uuid
from dataclasses import dataclass

from app.application.ports.repositories.user_repository import CareerProfileRepository
from app.domain.entities.user import CareerProfile
from app.domain.exceptions.domain_exceptions import DuplicateEntityError


@dataclass
class CreateProfileInput:
    user_id: uuid.UUID
    full_name: str
    email: str


class CreateProfileUseCase:
    def __init__(self, profile_repo: CareerProfileRepository) -> None:
        self._profile_repo = profile_repo

    async def execute(self, data: CreateProfileInput) -> CareerProfile:
        existing = await self._profile_repo.get_by_user_id(data.user_id)
        if existing:
            raise DuplicateEntityError("CareerProfile", "user_id")

        profile = CareerProfile(
            user_id=data.user_id,
            full_name=data.full_name,
            email=data.email,
        )
        return await self._profile_repo.create(profile)

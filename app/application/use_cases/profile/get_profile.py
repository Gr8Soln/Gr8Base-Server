import uuid

from app.application.ports.repositories.user_repository import CareerProfileRepository
from app.domain.entities.user import CareerProfile
from app.domain.exceptions.domain_exceptions import EntityNotFoundError


class GetProfileUseCase:
    def __init__(self, profile_repo: CareerProfileRepository) -> None:
        self._profile_repo = profile_repo

    async def execute(self, user_id: uuid.UUID) -> CareerProfile:
        profile = await self._profile_repo.get_by_user_id(user_id)
        if not profile:
            raise EntityNotFoundError("CareerProfile", str(user_id))
        return profile

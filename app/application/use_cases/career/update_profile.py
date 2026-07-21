import uuid
from dataclasses import dataclass

from app.application.ports.repositories.career_profile_repository import CareerProfileRepository
from app.domain.entities.career_profile import CareerProfile
from app.domain.exceptions.domain_exceptions import EntityNotFoundError


@dataclass
class UpdateCareerProfileInput:
    user_id: uuid.UUID
    full_name: str | None = None
    headline: str | None = None
    summary: str | None = None
    location: str | None = None
    phone: str | None = None
    address: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None
    website: str | None = None
    years_of_experience: int | None = None
    target_roles: list[str] | None = None
    target_industries: list[str] | None = None
    preferred_work_type: str | None = None
    writing_tone: str | None = None


class UpdateCareerProfileUseCase:
    def __init__(self, profile_repo: CareerProfileRepository) -> None:
        self._repo = profile_repo

    async def execute(self, data: UpdateCareerProfileInput) -> CareerProfile:
        profile = await self._repo.get_by_user_id(data.user_id)
        if not profile:
            raise EntityNotFoundError("CareerProfile", str(data.user_id))

        updatable = {
            "full_name",
            "headline",
            "summary",
            "location",
            "phone",
            "address",
            "linkedin_url",
            "github_url",
            "portfolio_url",
            "website",
            "years_of_experience",
            "target_roles",
            "target_industries",
            "preferred_work_type",
            "writing_tone",
        }
        for field_name in updatable:
            value = getattr(data, field_name, None)
            if value is not None:
                setattr(profile, field_name, value)

        return await self._repo.update(profile)

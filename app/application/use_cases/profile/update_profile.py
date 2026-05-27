import uuid
from dataclasses import dataclass

from app.application.ports.repositories.user_repository import CareerProfileRepository
from app.domain.entities.user import CareerProfile
from app.domain.exceptions.domain_exceptions import EntityNotFoundError


@dataclass
class UpdateProfileInput:
    user_id: uuid.UUID
    full_name: str | None = None
    headline: str | None = None
    summary: str | None = None
    location: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None
    years_of_experience: int | None = None
    target_roles: list[str] | None = None
    target_industries: list[str] | None = None
    target_salary_min: int | None = None
    target_salary_max: int | None = None
    preferred_work_type: str | None = None
    writing_tone: str | None = None


class UpdateProfileUseCase:
    def __init__(self, profile_repo: CareerProfileRepository) -> None:
        self._profile_repo = profile_repo

    async def execute(self, data: UpdateProfileInput) -> CareerProfile:
        profile = await self._profile_repo.get_by_user_id(data.user_id)
        if not profile:
            raise EntityNotFoundError("CareerProfile", str(data.user_id))

        # Only update fields that were explicitly provided
        if data.full_name is not None:
            profile.full_name = data.full_name
        if data.headline is not None:
            profile.headline = data.headline
        if data.summary is not None:
            profile.summary = data.summary
        if data.location is not None:
            profile.location = data.location
        if data.phone is not None:
            profile.phone = data.phone
        if data.linkedin_url is not None:
            profile.linkedin_url = data.linkedin_url
        if data.github_url is not None:
            profile.github_url = data.github_url
        if data.portfolio_url is not None:
            profile.portfolio_url = data.portfolio_url
        if data.years_of_experience is not None:
            profile.years_of_experience = data.years_of_experience
        if data.target_roles is not None:
            profile.target_roles = data.target_roles
        if data.target_industries is not None:
            profile.target_industries = data.target_industries
        if data.target_salary_min is not None:
            profile.target_salary_min = data.target_salary_min
        if data.target_salary_max is not None:
            profile.target_salary_max = data.target_salary_max
        if data.preferred_work_type is not None:
            profile.preferred_work_type = data.preferred_work_type
        if data.writing_tone is not None:
            profile.writing_tone = data.writing_tone

        return await self._profile_repo.update(profile)

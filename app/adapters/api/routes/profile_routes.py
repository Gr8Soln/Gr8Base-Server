from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.api.dependencies.auth import get_current_user
from app.adapters.api.schemas.profile_schemas import ProfileResponse, UpdateProfileRequest
from app.adapters.persistence.repositories.pg_user_repository import PgCareerProfileRepository
from app.application.use_cases.profile.get_profile import GetProfileUseCase
from app.application.use_cases.profile.update_profile import (
    UpdateProfileInput,
    UpdateProfileUseCase,
)
from app.domain.entities.user import CareerProfile, User
from app.infrastructure.database.connection import get_db_session

router = APIRouter()


def _profile_response(p: CareerProfile) -> ProfileResponse:
    return ProfileResponse(
        id=str(p.id),
        user_id=str(p.user_id),
        full_name=p.full_name,
        email=p.email,
        headline=p.headline,
        summary=p.summary,
        location=p.location,
        phone=p.phone,
        linkedin_url=p.linkedin_url,
        github_url=p.github_url,
        portfolio_url=p.portfolio_url,
        years_of_experience=p.years_of_experience,
        target_roles=p.target_roles,
        target_industries=p.target_industries,
        target_salary_min=p.target_salary_min,
        target_salary_max=p.target_salary_max,
        preferred_work_type=p.preferred_work_type,
        writing_tone=p.writing_tone,
    )


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ProfileResponse:
    use_case = GetProfileUseCase(PgCareerProfileRepository(session))
    profile = await use_case.execute(current_user.id)
    return _profile_response(profile)


@router.patch("/me", response_model=ProfileResponse)
async def update_my_profile(
    body: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ProfileResponse:
    use_case = UpdateProfileUseCase(PgCareerProfileRepository(session))
    profile = await use_case.execute(UpdateProfileInput(
        user_id=current_user.id,
        **body.model_dump(exclude_none=True),
    ))
    return _profile_response(profile)

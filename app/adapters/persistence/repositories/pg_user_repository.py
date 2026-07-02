import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.mappers.user_mapper import CareerProfileMapper, UserMapper
from app.adapters.persistence.models.career_profile_model import CareerProfileModel
from app.adapters.persistence.models.user_model import UserModel
from app.application.ports.repositories.user_repository import (
    CareerProfileRepository,
    UserRepository,
)
from app.domain.entities.user import CareerProfile, User
from app.domain.exceptions.domain_exceptions import EntityNotFoundError


class PgUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, user: User) -> User:
        model = UserMapper.to_model(user)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return UserMapper.to_entity(model)

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return UserMapper.to_entity(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email.lower())
        )
        model = result.scalar_one_or_none()
        return UserMapper.to_entity(model) if model else None

    async def update(self, user: User) -> User:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise EntityNotFoundError("User", str(user.id))

        model.email = user.email
        model.hashed_password = user.hashed_password
        model.full_name = user.full_name
        model.is_active = user.is_active
        model.is_verified = user.is_verified
        model.is_superuser = user.is_superuser
        await self._session.flush()
        await self._session.refresh(model)
        return UserMapper.to_entity(model)

    async def delete(self, user_id: uuid.UUID) -> None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()


class PgCareerProfileRepository(CareerProfileRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, profile: CareerProfile) -> CareerProfile:
        model = CareerProfileMapper.to_model(profile)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return CareerProfileMapper.to_entity(model)

    async def get_by_user_id(self, user_id: uuid.UUID) -> CareerProfile | None:
        result = await self._session.execute(
            select(CareerProfileModel).where(CareerProfileModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        return CareerProfileMapper.to_entity(model) if model else None

    async def update(self, profile: CareerProfile) -> CareerProfile:
        result = await self._session.execute(
            select(CareerProfileModel).where(CareerProfileModel.user_id == profile.user_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise EntityNotFoundError("CareerProfile", str(profile.user_id))

        model.full_name = profile.full_name
        model.email = profile.email
        model.headline = profile.headline
        model.summary = profile.summary
        model.location = profile.location
        model.phone = profile.phone
        model.linkedin_url = profile.linkedin_url
        model.github_url = profile.github_url
        model.portfolio_url = profile.portfolio_url
        model.years_of_experience = profile.years_of_experience
        model.target_roles = profile.target_roles
        model.target_industries = profile.target_industries
        model.target_salary_min = profile.target_salary_min
        model.target_salary_max = profile.target_salary_max
        model.preferred_work_type = profile.preferred_work_type
        model.writing_tone = profile.writing_tone
        await self._session.flush()
        await self._session.refresh(model)
        return CareerProfileMapper.to_entity(model)

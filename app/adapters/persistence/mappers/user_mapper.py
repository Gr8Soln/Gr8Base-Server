from app.adapters.persistence.models.career_profile_model import CareerProfileModel
from app.adapters.persistence.models.user_model import UserModel
from app.domain.entities.user import CareerProfile, User


class UserMapper:
    @staticmethod
    def to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            hashed_password=model.hashed_password,
            full_name=model.full_name,
            is_active=model.is_active,
            is_verified=model.is_verified,
            is_superuser=model.is_superuser,
        )

    @staticmethod
    def to_model(entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            email=entity.email,
            hashed_password=entity.hashed_password,
            full_name=entity.full_name,
            is_active=entity.is_active,
            is_verified=entity.is_verified,
            is_superuser=entity.is_superuser,
        )


class CareerProfileMapper:
    @staticmethod
    def to_entity(model: CareerProfileModel) -> CareerProfile:
        return CareerProfile(
            id=model.id,
            user_id=model.user_id,
            full_name=model.full_name,
            email=model.email,
            headline=model.headline,
            summary=model.summary,
            location=model.location,
            phone=model.phone,
            linkedin_url=model.linkedin_url,
            github_url=model.github_url,
            portfolio_url=model.portfolio_url,
            years_of_experience=model.years_of_experience,
            target_roles=model.target_roles or [],
            target_industries=model.target_industries or [],
            target_salary_min=model.target_salary_min,
            target_salary_max=model.target_salary_max,
            preferred_work_type=model.preferred_work_type,
            writing_tone=model.writing_tone,
        )

    @staticmethod
    def to_model(entity: CareerProfile) -> CareerProfileModel:
        return CareerProfileModel(
            id=entity.id,
            user_id=entity.user_id,
            full_name=entity.full_name,
            email=entity.email,
            headline=entity.headline,
            summary=entity.summary,
            location=entity.location,
            phone=entity.phone,
            linkedin_url=entity.linkedin_url,
            github_url=entity.github_url,
            portfolio_url=entity.portfolio_url,
            years_of_experience=entity.years_of_experience,
            target_roles=entity.target_roles,
            target_industries=entity.target_industries,
            target_salary_min=entity.target_salary_min,
            target_salary_max=entity.target_salary_max,
            preferred_work_type=entity.preferred_work_type,
            writing_tone=entity.writing_tone,
        )

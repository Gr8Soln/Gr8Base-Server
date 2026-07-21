from app.adapters.persistence.models.career_profile_model import CareerProfileModel
from app.domain.entities.career_profile import CareerProfile


class CareerProfileMapper:
    """Mapper for the canonical CareerProfile entity."""

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
            address=getattr(model, "address", ""),
            linkedin_url=model.linkedin_url,
            github_url=model.github_url,
            portfolio_url=model.portfolio_url,
            website=getattr(model, "website", ""),
            years_of_experience=model.years_of_experience,
            target_roles=model.target_roles or [],
            target_industries=model.target_industries or [],
            target_salary_min=model.target_salary_min,
            target_salary_max=model.target_salary_max,
            preferred_work_type=model.preferred_work_type,
            writing_tone=model.writing_tone,
            summary_embedding=getattr(model, "summary_embedding", None),
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
            address=entity.address,
            linkedin_url=entity.linkedin_url,
            github_url=entity.github_url,
            portfolio_url=entity.portfolio_url,
            website=entity.website,
            years_of_experience=entity.years_of_experience,
            target_roles=entity.target_roles,
            target_industries=entity.target_industries,
            target_salary_min=entity.target_salary_min,
            target_salary_max=entity.target_salary_max,
            preferred_work_type=entity.preferred_work_type,
            writing_tone=entity.writing_tone,
            summary_embedding=entity.summary_embedding,
        )

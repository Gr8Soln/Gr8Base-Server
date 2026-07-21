from app.adapters.persistence.models.skill_model import SkillModel
from app.domain.entities.skill import Skill
from app.domain.enums.skill_category import SkillCategory


class SkillMapper:
    @staticmethod
    def to_entity(model: SkillModel) -> Skill:
        return Skill(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            category=SkillCategory(model.category),
            proficiency=model.proficiency,
            years_of_experience=model.years_of_experience,
        )

    @staticmethod
    def to_model(entity: Skill) -> SkillModel:
        return SkillModel(
            id=entity.id,
            user_id=entity.user_id,
            name=entity.name,
            category=entity.category.value,
            proficiency=entity.proficiency,
            years_of_experience=entity.years_of_experience,
        )

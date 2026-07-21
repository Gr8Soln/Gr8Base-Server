from app.adapters.persistence.models.technology_model import TechnologyModel
from app.domain.entities.technology import Technology
from app.domain.enums.skill_category import SkillCategory


class TechnologyMapper:
    @staticmethod
    def to_entity(model: TechnologyModel) -> Technology:
        return Technology(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            category=SkillCategory(model.category),
            proficiency=model.proficiency,
        )

    @staticmethod
    def to_model(entity: Technology) -> TechnologyModel:
        return TechnologyModel(
            id=entity.id,
            user_id=entity.user_id,
            name=entity.name,
            category=entity.category.value,
            proficiency=entity.proficiency,
        )

from app.adapters.persistence.models.language_model import LanguageModel
from app.domain.entities.language import Language


class LanguageMapper:
    @staticmethod
    def to_entity(model: LanguageModel) -> Language:
        return Language(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            proficiency=model.proficiency,
        )

    @staticmethod
    def to_model(entity: Language) -> LanguageModel:
        return LanguageModel(
            id=entity.id,
            user_id=entity.user_id,
            name=entity.name,
            proficiency=entity.proficiency,
        )

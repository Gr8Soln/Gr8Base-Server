from app.adapters.persistence.models.award_model import AwardModel
from app.domain.entities.award import Award


class AwardMapper:
    @staticmethod
    def to_entity(model: AwardModel) -> Award:
        return Award(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            issuer=model.issuer,
            date=model.date,
            description=model.description,
        )

    @staticmethod
    def to_model(entity: Award) -> AwardModel:
        return AwardModel(
            id=entity.id,
            user_id=entity.user_id,
            name=entity.name,
            issuer=entity.issuer,
            date=entity.date,
            description=entity.description,
        )

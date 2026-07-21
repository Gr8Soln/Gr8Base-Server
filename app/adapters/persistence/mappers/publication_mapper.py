from app.adapters.persistence.models.publication_model import PublicationModel
from app.domain.entities.publication import Publication


class PublicationMapper:
    @staticmethod
    def to_entity(model: PublicationModel) -> Publication:
        return Publication(
            id=model.id,
            user_id=model.user_id,
            title=model.title,
            publisher=model.publisher,
            date=model.date,
            url=model.url,
            description=model.description,
        )

    @staticmethod
    def to_model(entity: Publication) -> PublicationModel:
        return PublicationModel(
            id=entity.id,
            user_id=entity.user_id,
            title=entity.title,
            publisher=entity.publisher,
            date=entity.date,
            url=entity.url,
            description=entity.description,
        )

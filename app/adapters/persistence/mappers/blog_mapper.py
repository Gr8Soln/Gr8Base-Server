from app.adapters.persistence.models.blog_model import BlogModel
from app.domain.entities.blog import Blog


class BlogMapper:
    @staticmethod
    def to_entity(model: BlogModel) -> Blog:
        return Blog(
            id=model.id,
            user_id=model.user_id,
            title=model.title,
            url=model.url,
            platform=model.platform,
            date=model.date,
            description=model.description,
        )

    @staticmethod
    def to_model(entity: Blog) -> BlogModel:
        return BlogModel(
            id=entity.id,
            user_id=entity.user_id,
            title=entity.title,
            url=entity.url,
            platform=entity.platform,
            date=entity.date,
            description=entity.description,
        )

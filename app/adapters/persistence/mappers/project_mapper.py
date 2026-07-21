from app.adapters.persistence.models.project_model import ProjectModel
from app.domain.entities.project import Project


class ProjectMapper:
    @staticmethod
    def to_entity(model: ProjectModel) -> Project:
        return Project(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            description=model.description,
            role=model.role,
            technologies=model.technologies or [],
            responsibilities=model.responsibilities or [],
            repository=model.repository,
            demo_url=model.demo_url,
            url=model.url,
            duration=model.duration,
            impact=model.impact,
            ai_summary=model.ai_summary,
            embedding=model.embedding,
        )

    @staticmethod
    def to_model(entity: Project) -> ProjectModel:
        return ProjectModel(
            id=entity.id,
            user_id=entity.user_id,
            name=entity.name,
            description=entity.description,
            role=entity.role,
            technologies=entity.technologies,
            responsibilities=entity.responsibilities,
            repository=entity.repository,
            demo_url=entity.demo_url,
            url=entity.url,
            duration=entity.duration,
            impact=entity.impact,
            ai_summary=entity.ai_summary,
            embedding=entity.embedding,
        )

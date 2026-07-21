import uuid

from app.adapters.persistence.models.experience_model import ExperienceModel
from app.domain.entities.experience import ImpactStatement, WorkExperience
from app.domain.enums.employment_type import EmploymentType


class ExperienceMapper:
    @staticmethod
    def to_entity(model: ExperienceModel) -> WorkExperience:
        return WorkExperience(
            id=model.id,
            user_id=model.user_id,
            company=model.company,
            role=model.role,
            start_date=model.start_date,
            end_date=model.end_date,
            is_current=model.is_current,
            location=model.location,
            description=model.description,
            employment_type=EmploymentType(model.employment_type),
            industry=model.industry,
            company_website=model.company_website,
            responsibilities=model.responsibilities or [],
            achievements=model.achievements or [],
            technologies=model.technologies or [],
            impact_statements=_deserialize_impacts(model.impact_statements or []),
            related_projects=_deserialize_uuids(model.related_projects or []),
            ai_summary=model.ai_summary,
            embedding=model.embedding,
            enrichment_data=model.enrichment_data or {},
        )

    @staticmethod
    def to_model(entity: WorkExperience) -> ExperienceModel:
        return ExperienceModel(
            id=entity.id,
            user_id=entity.user_id,
            company=entity.company,
            role=entity.role,
            start_date=entity.start_date,
            end_date=entity.end_date,
            is_current=entity.is_current,
            location=entity.location,
            description=entity.description,
            employment_type=entity.employment_type.value,
            industry=entity.industry,
            company_website=entity.company_website,
            responsibilities=entity.responsibilities,
            achievements=entity.achievements,
            technologies=entity.technologies,
            impact_statements=_serialize_impacts(entity.impact_statements),
            related_projects=[str(p) for p in entity.related_projects],
            ai_summary=entity.ai_summary,
            embedding=entity.embedding,
            enrichment_data=entity.enrichment_data,
        )


def _serialize_impacts(items: list[ImpactStatement]) -> list[dict]:
    return [
        {"problem": i.problem, "solution": i.solution, "result": i.result, "metric": i.metric}
        for i in items
    ]


def _deserialize_impacts(items: list[dict]) -> list[ImpactStatement]:
    return [
        ImpactStatement(
            problem=i.get("problem", ""),
            solution=i.get("solution", ""),
            result=i.get("result", ""),
            metric=i.get("metric", ""),
        )
        for i in items
    ]


def _deserialize_uuids(items: list) -> list[uuid.UUID]:
    result: list[uuid.UUID] = []
    for item in items:
        if isinstance(item, uuid.UUID):
            result.append(item)
        elif isinstance(item, str):
            result.append(uuid.UUID(item))
    return result

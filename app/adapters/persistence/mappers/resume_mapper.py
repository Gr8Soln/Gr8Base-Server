import uuid

from app.adapters.persistence.models.resume_model import ResumeModel
from app.domain.entities.resume import (
    Certification,
    Education,
    ImpactStatement,
    Project,
    Resume,
    WorkExperience,
)
from app.domain.enums.resume_strategy import ResumeStrategy


class ResumeMapper:
    @staticmethod
    def to_entity(model: ResumeModel) -> Resume:
        return Resume(
            id=model.id,
            user_id=model.user_id,
            file_url=model.file_url,
            file_name=model.file_name,
            raw_text=model.raw_text,
            skills=model.skills or [],
            experience=_deserialize_experience(model.experience or []),
            projects=_deserialize_projects(model.projects or []),
            education=_deserialize_education(model.education or []),
            certifications=_deserialize_certifications(model.certifications or []),
            languages=model.languages or [],
            version=model.version,
            label=model.label,
            strategy=ResumeStrategy(model.strategy) if model.strategy else None,
            parent_resume_id=model.parent_resume_id,
            ats_score_snapshot=model.ats_score_snapshot,
        )

    @staticmethod
    def to_model(entity: Resume) -> ResumeModel:
        return ResumeModel(
            id=entity.id,
            user_id=entity.user_id,
            file_url=entity.file_url,
            file_name=entity.file_name,
            raw_text=entity.raw_text,
            skills=entity.skills,
            experience=_serialize_experience(entity.experience),
            projects=_serialize_projects(entity.projects),
            education=_serialize_education(entity.education),
            certifications=_serialize_certifications(entity.certifications),
            languages=entity.languages,
            version=entity.version,
            label=entity.label,
            strategy=entity.strategy.value if entity.strategy else None,
            parent_resume_id=entity.parent_resume_id,
            ats_score_snapshot=entity.ats_score_snapshot,
        )


# ── Serializers (entity → JSON-safe dict) ────────────────────────────────────

def _serialize_experience(items: list[WorkExperience]) -> list[dict]:
    return [
        {
            "id": str(e.id),
            "company": e.company,
            "role": e.role,
            "start_date": e.start_date,
            "end_date": e.end_date,
            "is_current": e.is_current,
            "location": e.location,
            "description": e.description,
            "technologies": e.technologies,
            "impact_statements": [
                {
                    "problem": i.problem,
                    "solution": i.solution,
                    "result": i.result,
                    "metric": i.metric,
                }
                for i in e.impact_statements
            ],
        }
        for e in items
    ]


def _serialize_projects(items: list[Project]) -> list[dict]:
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "description": p.description,
            "technologies": p.technologies,
            "url": p.url,
            "impact": p.impact,
        }
        for p in items
    ]


def _serialize_education(items: list[Education]) -> list[dict]:
    return [
        {
            "id": str(e.id),
            "institution": e.institution,
            "degree": e.degree,
            "field_of_study": e.field_of_study,
            "start_year": e.start_year,
            "end_year": e.end_year,
            "gpa": e.gpa,
            "honors": e.honors,
        }
        for e in items
    ]


def _serialize_certifications(items: list[Certification]) -> list[dict]:
    return [
        {
            "id": str(c.id),
            "name": c.name,
            "issuer": c.issuer,
            "issue_date": c.issue_date,
            "expiry_date": c.expiry_date,
            "credential_url": c.credential_url,
        }
        for c in items
    ]


# ── Deserializers (JSON dict → entity) ───────────────────────────────────────

def _deserialize_experience(items: list[dict]) -> list[WorkExperience]:
    result = []
    for e in items:
        impacts = [
            ImpactStatement(
                problem=i.get("problem", ""),
                solution=i.get("solution", ""),
                result=i.get("result", ""),
                metric=i.get("metric", ""),
            )
            for i in e.get("impact_statements", [])
        ]
        result.append(
            WorkExperience(
                id=uuid.UUID(e["id"]) if "id" in e else uuid.uuid4(),
                company=e.get("company", ""),
                role=e.get("role", ""),
                start_date=e.get("start_date", ""),
                end_date=e.get("end_date"),
                is_current=e.get("is_current", False),
                location=e.get("location", ""),
                description=e.get("description", ""),
                technologies=e.get("technologies", []),
                impact_statements=impacts,
            )
        )
    return result


def _deserialize_projects(items: list[dict]) -> list[Project]:
    return [
        Project(
            id=uuid.UUID(p["id"]) if "id" in p else uuid.uuid4(),
            name=p.get("name", ""),
            description=p.get("description", ""),
            technologies=p.get("technologies", []),
            url=p.get("url", ""),
            impact=p.get("impact", ""),
        )
        for p in items
    ]


def _deserialize_education(items: list[dict]) -> list[Education]:
    return [
        Education(
            id=uuid.UUID(e["id"]) if "id" in e else uuid.uuid4(),
            institution=e.get("institution", ""),
            degree=e.get("degree", ""),
            field_of_study=e.get("field_of_study", ""),
            start_year=e.get("start_year"),
            end_year=e.get("end_year"),
            gpa=e.get("gpa"),
            honors=e.get("honors", ""),
        )
        for e in items
    ]


def _deserialize_certifications(items: list[dict]) -> list[Certification]:
    return [
        Certification(
            id=uuid.UUID(c["id"]) if "id" in c else uuid.uuid4(),
            name=c.get("name", ""),
            issuer=c.get("issuer", ""),
            issue_date=c.get("issue_date", ""),
            expiry_date=c.get("expiry_date", ""),
            credential_url=c.get("credential_url", ""),
        )
        for c in items
    ]

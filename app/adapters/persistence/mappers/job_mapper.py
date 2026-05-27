from app.adapters.persistence.models.job_model import JobModel
from app.domain.entities.job import JobDescription


class JobMapper:
    @staticmethod
    def to_entity(model: JobModel) -> JobDescription:
        return JobDescription(
            id=model.id,
            user_id=model.user_id,
            raw_text=model.raw_text,
            title=model.title,
            company=model.company,
            company_url=model.company_url,
            location=model.location,
            work_type=model.work_type,
            role=model.role,
            seniority=model.seniority,
            domain=model.domain,
            required_skills=model.required_skills or [],
            preferred_skills=model.preferred_skills or [],
            soft_skills=model.soft_skills or [],
            tools_and_technologies=model.tools_and_technologies or [],
            ats_keywords=model.ats_keywords or [],
            hidden_signals=model.hidden_signals or [],
            salary_min=model.salary_min,
            salary_max=model.salary_max,
            embedding=None,  # loaded separately from vector column
        )

    @staticmethod
    def to_model(entity: JobDescription) -> JobModel:
        return JobModel(
            id=entity.id,
            user_id=entity.user_id,
            raw_text=entity.raw_text,
            title=entity.title,
            company=entity.company,
            company_url=entity.company_url,
            location=entity.location,
            work_type=entity.work_type,
            role=entity.role,
            seniority=entity.seniority,
            domain=entity.domain,
            required_skills=entity.required_skills,
            preferred_skills=entity.preferred_skills,
            soft_skills=entity.soft_skills,
            tools_and_technologies=entity.tools_and_technologies,
            ats_keywords=entity.ats_keywords,
            hidden_signals=entity.hidden_signals,
            salary_min=entity.salary_min,
            salary_max=entity.salary_max,
        )

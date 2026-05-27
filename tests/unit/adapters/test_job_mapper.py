import uuid

from app.adapters.persistence.mappers.job_mapper import JobMapper
from app.adapters.persistence.models.job_model import JobModel
from app.domain.entities.job import JobDescription


def _make_job_model() -> JobModel:
    return JobModel(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        raw_text="Senior Backend Engineer at TechCorp...",
        title="Senior Backend Engineer",
        company="TechCorp",
        company_url="https://techcorp.com",
        location="Lagos, Nigeria",
        work_type="remote",
        role="Backend Engineer",
        seniority="Senior",
        domain="Fintech",
        required_skills=["Python", "FastAPI", "PostgreSQL"],
        preferred_skills=["Redis", "Docker"],
        soft_skills=["Communication"],
        tools_and_technologies=["Python", "FastAPI", "PostgreSQL", "Redis"],
        ats_keywords=["python", "fastapi", "backend engineer"],
        hidden_signals=["Fast-paced", "Autonomous"],
        salary_min=80000,
        salary_max=120000,
    )


def test_job_model_to_entity() -> None:
    model = _make_job_model()
    entity = JobMapper.to_entity(model)

    assert entity.id == model.id
    assert entity.user_id == model.user_id
    assert entity.title == "Senior Backend Engineer"
    assert entity.seniority == "Senior"
    assert "Python" in entity.required_skills
    assert entity.salary_min == 80000
    assert entity.embedding is None  # loaded separately


def test_job_entity_to_model() -> None:
    job = JobDescription(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        raw_text="We are looking for a Backend Engineer...",
        title="Backend Engineer",
        company="StartupX",
        role="Backend Engineer",
        seniority="Mid-Level",
        domain="SaaS",
        required_skills=["Go", "PostgreSQL"],
        ats_keywords=["golang", "backend"],
    )
    model = JobMapper.to_model(job)

    assert model.id == job.id
    assert model.title == "Backend Engineer"
    assert model.required_skills == ["Go", "PostgreSQL"]
    assert model.ats_keywords == ["golang", "backend"]


def test_job_roundtrip_preserves_all_lists() -> None:
    model = _make_job_model()
    entity = JobMapper.to_entity(model)
    restored = JobMapper.to_model(entity)

    assert restored.required_skills == model.required_skills
    assert restored.preferred_skills == model.preferred_skills
    assert restored.ats_keywords == model.ats_keywords
    assert restored.hidden_signals == model.hidden_signals
    assert restored.tools_and_technologies == model.tools_and_technologies

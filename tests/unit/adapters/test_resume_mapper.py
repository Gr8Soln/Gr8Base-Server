import uuid

from app.adapters.persistence.mappers.resume_mapper import (
    ResumeMapper,
    _deserialize_experience,
    _serialize_experience,
)
from app.domain.entities.resume import (
    ImpactStatement,
    Project,
    Resume,
    WorkExperience,
)
from app.domain.enums.resume_strategy import ResumeStrategy


def _make_resume(user_id: uuid.UUID | None = None) -> Resume:
    uid = user_id or uuid.uuid4()
    return Resume(
        id=uuid.uuid4(),
        user_id=uid,
        file_url="https://r2.example.com/resume.pdf",
        file_name="resume.pdf",
        raw_text="John Doe, Software Engineer",
        skills=["Python", "FastAPI", "PostgreSQL"],
        experience=[
            WorkExperience(
                id=uuid.uuid4(),
                company="Acme Corp",
                role="Backend Engineer",
                start_date="2023-01",
                end_date="2025-01",
                is_current=False,
                location="Lagos, Nigeria",
                description="Built APIs",
                technologies=["Python", "FastAPI"],
                impact_statements=[
                    ImpactStatement(
                        problem="Slow API",
                        solution="Added Redis caching",
                        result="40% latency reduction",
                        metric="40%",
                    )
                ],
            )
        ],
        projects=[
            Project(
                id=uuid.uuid4(),
                name="NovaAcademy",
                description="RAG learning platform",
                technologies=["Python", "Qdrant"],
                url="https://github.com/Gr8Soln/nova",
                impact="Served 500+ students",
            )
        ],
        version=1,
        label="Backend Resume",
        strategy=ResumeStrategy.ATS_AGGRESSIVE,
    )


def test_resume_entity_to_model_roundtrip() -> None:
    resume = _make_resume()
    model = ResumeMapper.to_model(resume)

    assert model.id == resume.id
    assert model.user_id == resume.user_id
    assert model.file_name == "resume.pdf"
    assert model.skills == ["Python", "FastAPI", "PostgreSQL"]
    assert model.strategy == "ats_aggressive"
    assert len(model.experience) == 1
    assert model.experience[0]["company"] == "Acme Corp"
    assert model.experience[0]["impact_statements"][0]["metric"] == "40%"


def test_resume_model_to_entity_roundtrip() -> None:
    resume = _make_resume()
    model = ResumeMapper.to_model(resume)
    restored = ResumeMapper.to_entity(model)

    assert restored.id == resume.id
    assert restored.skills == resume.skills
    assert len(restored.experience) == 1
    assert restored.experience[0].company == "Acme Corp"
    assert restored.experience[0].impact_statements[0].metric == "40%"
    assert len(restored.projects) == 1
    assert restored.projects[0].name == "NovaAcademy"
    assert restored.strategy == ResumeStrategy.ATS_AGGRESSIVE


def test_serialize_experience_preserves_all_fields() -> None:
    exp = WorkExperience(
        id=uuid.uuid4(),
        company="TechCorp",
        role="AI Engineer",
        start_date="2024-01",
        end_date=None,
        is_current=True,
        location="Remote",
        description="Built LLM pipelines",
        technologies=["Python", "LangGraph"],
        impact_statements=[
            ImpactStatement(problem="P", solution="S", result="R", metric="10x")
        ],
    )
    serialized = _serialize_experience([exp])
    assert len(serialized) == 1
    assert serialized[0]["is_current"] is True
    assert serialized[0]["end_date"] is None
    assert serialized[0]["impact_statements"][0]["metric"] == "10x"


def test_deserialize_experience_handles_missing_id() -> None:
    raw = [
        {
            "company": "StartupX",
            "role": "Dev",
            "start_date": "2022-06",
            "end_date": "2023-06",
            "is_current": False,
            "location": "",
            "description": "",
            "technologies": [],
            "impact_statements": [],
        }
    ]
    result = _deserialize_experience(raw)
    assert len(result) == 1
    assert result[0].company == "StartupX"
    assert isinstance(result[0].id, uuid.UUID)


def test_model_with_null_strategy() -> None:
    resume = _make_resume()
    resume.strategy = None
    model = ResumeMapper.to_model(resume)
    assert model.strategy is None
    restored = ResumeMapper.to_entity(model)
    assert restored.strategy is None

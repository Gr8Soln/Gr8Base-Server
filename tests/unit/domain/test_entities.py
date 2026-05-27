import uuid

from app.domain.entities.application import JobApplication
from app.domain.entities.ats import ATSScore, ScoreDimension
from app.domain.entities.job import JobDescription
from app.domain.entities.resume import ImpactStatement, Resume, WorkExperience
from app.domain.entities.user import CareerProfile
from app.domain.enums.application_stage import ApplicationStage


def test_resume_entity_defaults() -> None:
    user_id = uuid.uuid4()
    resume = Resume(
        user_id=user_id,
        file_url="https://r2.example.com/resume.pdf",
        file_name="resume.pdf",
        raw_text="John Doe, Software Engineer...",
    )
    assert resume.user_id == user_id
    assert resume.version == 1
    assert resume.skills == []
    assert resume.experience == []
    assert resume.projects == []
    assert resume.embedding is None
    assert isinstance(resume.id, uuid.UUID)


def test_work_experience_with_impact() -> None:
    impact = ImpactStatement(
        problem="Slow API response times",
        solution="Implemented async caching with Redis",
        result="Reduced latency by 40%",
        metric="40%",
    )
    exp = WorkExperience(
        company="Acme Corp",
        role="Backend Engineer",
        start_date="2023-01",
        end_date="2025-01",
        impact_statements=[impact],
        technologies=["Python", "FastAPI", "Redis"],
    )
    assert exp.company == "Acme Corp"
    assert len(exp.impact_statements) == 1
    assert exp.impact_statements[0].metric == "40%"


def test_job_description_entity() -> None:
    job = JobDescription(
        user_id=uuid.uuid4(),
        raw_text="We are looking for a backend engineer...",
        title="Backend Engineer",
        company="TechCorp",
        seniority="Mid-Level",
        domain="Fintech",
        required_skills=["Python", "Docker"],
        soft_skills=["Communication"],
    )
    assert job.title == "Backend Engineer"
    assert "Python" in job.required_skills


def test_ats_score_entity() -> None:
    user_id = uuid.uuid4()
    resume_id = uuid.uuid4()
    job_id = uuid.uuid4()

    score = ATSScore(
        resume_id=resume_id,
        job_id=job_id,
        user_id=user_id,
        overall_score=78.5,
        dimensions=[
            ScoreDimension(
                name="keyword_match",
                score=0.82,
                weight=0.25,
                feedback="Good keyword coverage",
            )
        ],
        missing_keywords=["kubernetes", "terraform"],
        is_ats_safe=True,
    )
    assert score.overall_score == 78.5
    assert len(score.dimensions) == 1
    assert score.dimensions[0].name == "keyword_match"


def test_job_application_stage_transitions() -> None:
    app = JobApplication(
        user_id=uuid.uuid4(),
        job_title="Backend Engineer",
        company="TechCorp",
    )
    assert app.stage == ApplicationStage.SAVED

    app.stage = ApplicationStage.APPLIED
    assert app.stage == ApplicationStage.APPLIED

    app.stage = ApplicationStage.INTERVIEW
    assert app.stage == ApplicationStage.INTERVIEW


def test_career_profile_defaults() -> None:
    profile = CareerProfile(
        user_id=uuid.uuid4(),
        full_name="Emmanuel",
        email="emmanuel@example.com",
    )
    assert profile.target_roles == []
    assert profile.years_of_experience == 0
    assert profile.writing_tone == "professional"

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.application.use_cases.resume.compare_resume_versions import CompareResumeVersionsUseCase
from app.application.use_cases.resume.generate_resume_pdf import (
    GeneratePDFInput,
    GenerateResumePDFUseCase,
)
from app.application.use_cases.resume.optimize_resume import (
    OptimizeResumeInput,
    OptimizeResumeUseCase,
)
from app.application.use_cases.resume.rollback_resume_version import RollbackResumeVersionUseCase
from app.domain.entities.job import JobDescription
from app.domain.entities.resume import ImpactStatement, Resume, WorkExperience
from app.domain.enums.resume_strategy import ResumeStrategy
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, UnauthorizedError


def _make_resume(
    user_id: uuid.UUID, version: int = 1, parent_id: uuid.UUID | None = None
) -> Resume:
    return Resume(
        id=uuid.uuid4(), user_id=user_id,
        file_url="https://r2.example.com/resume.pdf",
        file_name="resume.pdf", raw_text="Python engineer",
        skills=["Python", "FastAPI"],
        experience=[
            WorkExperience(
                id=uuid.uuid4(), company="Acme", role="Engineer",
                start_date="2022-01", end_date="2024-01",
                impact_statements=[
                    ImpactStatement(problem="P", solution="S", result="R", metric="40%")
                ],
                technologies=["Python"],
            )
        ],
        version=version, parent_resume_id=parent_id,
        ats_score_snapshot=65.0 if version == 1 else 78.0,
    )


def _make_job(user_id: uuid.UUID) -> JobDescription:
    return JobDescription(
        id=uuid.uuid4(), user_id=user_id,
        raw_text="Senior Backend Engineer",
        title="Senior Backend Engineer", role="Backend Engineer",
        seniority="Senior", domain="Fintech",
        required_skills=["Python", "FastAPI"],
        ats_keywords=["python", "fastapi"],
    )


# ── Optimize ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_optimize_resume_creates_new_version() -> None:
    user_id = uuid.uuid4()
    resume = _make_resume(user_id)
    job = _make_job(user_id)
    optimized = _make_resume(user_id, version=2, parent_id=resume.id)

    resume_repo = MagicMock()
    resume_repo.get_by_id = AsyncMock(return_value=resume)
    resume_repo.create = AsyncMock(return_value=optimized)

    job_repo = MagicMock()
    job_repo.get_by_id = AsyncMock(return_value=job)

    mock_state = {
        "post_ats_score": 78.0,
        "critique_passed": True,
        "critique_feedback": "Good resume",
        "optimized_resume": {
            "skills": ["Python", "FastAPI", "Redis"],
            "experience": [{"company": "Acme", "role": "Engineer",
                            "start_date": "2022-01", "end_date": "2024-01",
                            "impact_statements": [], "technologies": ["Python"],
                            "optimized_bullets": ["Built scalable Python APIs"]}],
            "projects": [], "section_order": ["skills", "experience"],
            "languages": [], "tone": "professional",
        },
        "weak_points": [],
    }

    with patch(
        "app.application.use_cases.resume.optimize_resume.get_resume_optimization_workflow"
    ) as mock_wf:
        mock_workflow = MagicMock()
        mock_workflow.ainvoke = AsyncMock(return_value=mock_state)
        mock_wf.return_value = mock_workflow

        uc = OptimizeResumeUseCase(resume_repo=resume_repo, job_repo=job_repo)
        result = await uc.execute(OptimizeResumeInput(
            resume_id=resume.id, job_id=job.id, user_id=user_id,
            strategy=ResumeStrategy.ATS_AGGRESSIVE,
        ))

    resume_repo.create.assert_called_once()
    assert result.version == 2
    assert result.parent_resume_id == resume.id


@pytest.mark.asyncio
async def test_optimize_resume_wrong_user_raises() -> None:
    user_id = uuid.uuid4()
    resume = _make_resume(user_id)

    resume_repo = MagicMock()
    resume_repo.get_by_id = AsyncMock(return_value=resume)
    job_repo = MagicMock()

    uc = OptimizeResumeUseCase(resume_repo, job_repo)
    with pytest.raises(UnauthorizedError):
        await uc.execute(OptimizeResumeInput(
            resume_id=resume.id, job_id=uuid.uuid4(), user_id=uuid.uuid4(),
        ))


# ── Compare ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_compare_versions_shows_skill_delta() -> None:
    user_id = uuid.uuid4()
    base = _make_resume(user_id, version=1)
    base.skills = ["Python", "FastAPI"]
    base.ats_score_snapshot = 65.0

    optimized = _make_resume(user_id, version=2, parent_id=base.id)
    optimized.skills = ["Python", "FastAPI", "Redis", "Docker"]
    optimized.ats_score_snapshot = 78.5

    resume_repo = MagicMock()
    resume_repo.get_by_id = AsyncMock(side_effect=lambda rid: (
        base if rid == base.id else optimized
    ))

    uc = CompareResumeVersionsUseCase(resume_repo)
    comparison = await uc.execute(
        base_id=base.id, optimized_id=optimized.id, user_id=user_id
    )

    assert "redis" in comparison.added_skills
    assert "docker" in comparison.added_skills
    assert comparison.removed_skills == []
    assert comparison.ats_score_delta == 13.5


# ── Rollback ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_rollback_returns_parent() -> None:
    user_id = uuid.uuid4()
    parent = _make_resume(user_id, version=1)
    child = _make_resume(user_id, version=2, parent_id=parent.id)

    resume_repo = MagicMock()
    resume_repo.get_by_id = AsyncMock(side_effect=lambda rid: (
        child if rid == child.id else parent
    ))

    uc = RollbackResumeVersionUseCase(resume_repo)
    result = await uc.execute(resume_id=child.id, user_id=user_id)
    assert result.id == parent.id
    assert result.version == 1


@pytest.mark.asyncio
async def test_rollback_no_parent_raises() -> None:
    user_id = uuid.uuid4()
    resume = _make_resume(user_id)  # no parent_resume_id

    resume_repo = MagicMock()
    resume_repo.get_by_id = AsyncMock(return_value=resume)

    uc = RollbackResumeVersionUseCase(resume_repo)
    with pytest.raises(EntityNotFoundError):
        await uc.execute(resume_id=resume.id, user_id=user_id)


# ── PDF Generation ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_generate_pdf_calls_renderer() -> None:
    user_id = uuid.uuid4()
    resume = _make_resume(user_id)

    resume_repo = MagicMock()
    resume_repo.get_by_id = AsyncMock(return_value=resume)

    renderer = MagicMock()
    renderer.render = AsyncMock(return_value="https://r2.example.com/pdfs/resume.pdf")

    uc = GenerateResumePDFUseCase(resume_repo=resume_repo, renderer=renderer)
    result = await uc.execute(GeneratePDFInput(
        resume_id=resume.id, user_id=user_id, template="classic"
    ))

    renderer.render.assert_called_once_with(resume_id=resume.id, template="classic")
    assert result.pdf_url == "https://r2.example.com/pdfs/resume.pdf"
    assert result.template == "classic"


@pytest.mark.asyncio
async def test_generate_pdf_wrong_user_raises() -> None:
    user_id = uuid.uuid4()
    resume = _make_resume(user_id)

    resume_repo = MagicMock()
    resume_repo.get_by_id = AsyncMock(return_value=resume)
    renderer = MagicMock()

    uc = GenerateResumePDFUseCase(resume_repo=resume_repo, renderer=renderer)
    with pytest.raises(UnauthorizedError):
        await uc.execute(GeneratePDFInput(
            resume_id=resume.id, user_id=uuid.uuid4(), template="classic"
        ))

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.application.use_cases.ats.get_ats_score import GetATSScoreUseCase
from app.application.use_cases.ats.score_resume import ScoreResumeInput, ScoreResumeUseCase
from app.domain.entities.ats import ATSScore, ScoreDimension
from app.domain.entities.job import JobDescription
from app.domain.entities.resume import Resume
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, UnauthorizedError


def _make_resume(user_id: uuid.UUID) -> Resume:
    return Resume(
        id=uuid.uuid4(),
        user_id=user_id,
        file_url="https://r2.example.com/resume.pdf",
        file_name="resume.pdf",
        raw_text="Python FastAPI backend engineer",
        skills=["Python", "FastAPI"],
    )


def _make_job(user_id: uuid.UUID) -> JobDescription:
    return JobDescription(
        id=uuid.uuid4(),
        user_id=user_id,
        raw_text="Senior Backend Engineer",
        title="Senior Backend Engineer",
        role="Backend Engineer",
        seniority="Senior",
        required_skills=["Python", "FastAPI"],
        ats_keywords=["python", "fastapi"],
    )


def _make_score(user_id: uuid.UUID, resume_id: uuid.UUID, job_id: uuid.UUID) -> ATSScore:
    return ATSScore(
        id=uuid.uuid4(),
        user_id=user_id,
        resume_id=resume_id,
        job_id=job_id,
        overall_score=78.5,
        dimensions=[
            ScoreDimension(name="keyword_match", score=0.85, weight=0.25)
        ],
        missing_keywords=["docker"],
        recommendations=["Add Docker to skills"],
        is_ats_safe=True,
    )


@pytest.mark.asyncio
async def test_score_resume_not_found_raises() -> None:
    user_id = uuid.uuid4()

    ats_repo = MagicMock()
    resume_repo = MagicMock()
    resume_repo.get_by_id = AsyncMock(return_value=None)
    job_repo = MagicMock()

    use_case = ScoreResumeUseCase(ats_repo, resume_repo, job_repo)

    with pytest.raises(EntityNotFoundError):
        await use_case.execute(
            ScoreResumeInput(resume_id=uuid.uuid4(), job_id=uuid.uuid4(), user_id=user_id)
        )


@pytest.mark.asyncio
async def test_score_resume_wrong_user_raises() -> None:
    user_id = uuid.uuid4()
    attacker_id = uuid.uuid4()
    resume = _make_resume(user_id)

    ats_repo = MagicMock()
    resume_repo = MagicMock()
    resume_repo.get_by_id = AsyncMock(return_value=resume)
    job_repo = MagicMock()

    use_case = ScoreResumeUseCase(ats_repo, resume_repo, job_repo)

    with pytest.raises(UnauthorizedError):
        await use_case.execute(
            ScoreResumeInput(
                resume_id=resume.id, job_id=uuid.uuid4(), user_id=attacker_id
            )
        )


@pytest.mark.asyncio
async def test_score_resume_job_not_found_raises() -> None:
    user_id = uuid.uuid4()
    resume = _make_resume(user_id)

    ats_repo = MagicMock()
    resume_repo = MagicMock()
    resume_repo.get_by_id = AsyncMock(return_value=resume)
    job_repo = MagicMock()
    job_repo.get_by_id = AsyncMock(return_value=None)

    use_case = ScoreResumeUseCase(ats_repo, resume_repo, job_repo)

    with pytest.raises(EntityNotFoundError):
        await use_case.execute(
            ScoreResumeInput(resume_id=resume.id, job_id=uuid.uuid4(), user_id=user_id)
        )


@pytest.mark.asyncio
async def test_score_resume_runs_workflow_and_persists() -> None:
    user_id = uuid.uuid4()
    resume = _make_resume(user_id)
    job = _make_job(user_id)
    score = _make_score(user_id, resume.id, job.id)

    ats_repo = MagicMock()
    ats_repo.create = AsyncMock(return_value=score)
    resume_repo = MagicMock()
    resume_repo.get_by_id = AsyncMock(return_value=resume)
    job_repo = MagicMock()
    job_repo.get_by_id = AsyncMock(return_value=job)

    mock_final_state = {
        "overall_score": 78.5,
        "dimension_breakdown": {
            "keyword_match": {"score": 85.0, "weight": 0.25, "weighted_contribution": 21.25}
        },
        "missing_skills": ["docker"],
        "weak_sections": [],
        "recommendations": ["Add Docker"],
        "recruiter_critique": "Good candidate",
        "is_ats_safe": True,
        "keyword_gaps": [],
    }

    with patch(
        "app.application.use_cases.ats.score_resume.get_ats_scoring_workflow"
    ) as mock_workflow_fn:
        mock_workflow = MagicMock()
        mock_workflow.ainvoke = AsyncMock(return_value=mock_final_state)
        mock_workflow_fn.return_value = mock_workflow

        use_case = ScoreResumeUseCase(ats_repo, resume_repo, job_repo)
        result = await use_case.execute(
            ScoreResumeInput(resume_id=resume.id, job_id=job.id, user_id=user_id)
        )

    ats_repo.create.assert_called_once()
    assert result.overall_score == 78.5
    assert "docker" in result.missing_keywords


@pytest.mark.asyncio
async def test_get_ats_score_not_found_raises() -> None:
    ats_repo = MagicMock()
    ats_repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(EntityNotFoundError):
        await GetATSScoreUseCase(ats_repo).execute(uuid.uuid4(), uuid.uuid4())


@pytest.mark.asyncio
async def test_get_ats_score_wrong_user_raises() -> None:
    user_id = uuid.uuid4()
    score = _make_score(user_id, uuid.uuid4(), uuid.uuid4())

    ats_repo = MagicMock()
    ats_repo.get_by_id = AsyncMock(return_value=score)

    with pytest.raises(UnauthorizedError):
        await GetATSScoreUseCase(ats_repo).execute(score.id, uuid.uuid4())

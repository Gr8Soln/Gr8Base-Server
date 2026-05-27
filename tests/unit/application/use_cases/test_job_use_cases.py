import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.use_cases.jobs.analyze_job_description import (
    AnalyzeJobDescriptionUseCase,
    AnalyzeJobInput,
)
from app.application.use_cases.jobs.extract_keywords import ExtractKeywordsUseCase
from app.application.use_cases.jobs.get_job import GetJobUseCase
from app.domain.entities.job import JobDescription
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, UnauthorizedError


def _make_job(user_id: uuid.UUID | None = None) -> JobDescription:
    uid = user_id or uuid.uuid4()
    return JobDescription(
        id=uuid.uuid4(),
        user_id=uid,
        raw_text="Senior Backend Engineer with Python and FastAPI",
        title="Senior Backend Engineer",
        role="Backend Engineer",
        seniority="Senior",
        domain="Fintech",
        required_skills=["Python", "FastAPI", "PostgreSQL"],
        preferred_skills=["Redis"],
        tools_and_technologies=["Python", "FastAPI"],
        ats_keywords=["python", "fastapi", "backend engineer"],
        soft_skills=["Communication"],
    )


# ── Analyze ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_analyze_jd_creates_and_analyzes() -> None:
    user_id = uuid.uuid4()
    job = _make_job(user_id)

    repo = MagicMock()
    repo.create = AsyncMock(return_value=job)
    repo.update = AsyncMock(return_value=job)

    analyzer = MagicMock()
    analyzer.analyze = AsyncMock(return_value=job)

    use_case = AnalyzeJobDescriptionUseCase(job_repo=repo, analyzer=analyzer)
    result = await use_case.execute(
        AnalyzeJobInput(
            user_id=user_id,
            raw_text="Senior Backend Engineer with Python...",
        )
    )

    repo.create.assert_called_once()
    analyzer.analyze.assert_called_once()
    repo.update.assert_called_once()
    assert result.seniority == "Senior"
    assert "Python" in result.required_skills


# ── Get ───────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_job_returns_correct_job() -> None:
    user_id = uuid.uuid4()
    job = _make_job(user_id)

    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=job)

    use_case = GetJobUseCase(repo)
    result = await use_case.execute(job_id=job.id, user_id=user_id)
    assert result.id == job.id


@pytest.mark.asyncio
async def test_get_job_not_found_raises() -> None:
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(EntityNotFoundError):
        await GetJobUseCase(repo).execute(uuid.uuid4(), uuid.uuid4())


@pytest.mark.asyncio
async def test_get_job_wrong_user_raises() -> None:
    job = _make_job()
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=job)

    with pytest.raises(UnauthorizedError):
        await GetJobUseCase(repo).execute(job.id, uuid.uuid4())


# ── Keywords ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_extract_keywords_deduplicates_and_orders() -> None:
    user_id = uuid.uuid4()
    job = _make_job(user_id)

    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=job)

    use_case = ExtractKeywordsUseCase(repo)
    keywords = await use_case.execute(job_id=job.id, user_id=user_id)

    # ATS keywords first, then required skills, then tools — deduplicated
    assert len(keywords) == len(set(k.lower() for k in keywords))
    assert len(keywords) > 0
    # "python" from ats_keywords should appear before "Python" from required_skills
    lower_kws = [k.lower() for k in keywords]
    assert "python" in lower_kws
    assert "fastapi" in lower_kws


@pytest.mark.asyncio
async def test_extract_keywords_wrong_user_raises() -> None:
    job = _make_job()
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=job)

    with pytest.raises(UnauthorizedError):
        await ExtractKeywordsUseCase(repo).execute(job.id, uuid.uuid4())

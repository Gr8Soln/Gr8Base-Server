import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.use_cases.resume.get_resume import GetResumeUseCase
from app.application.use_cases.resume.list_resume_versions import ListResumeVersionsUseCase
from app.application.use_cases.resume.parse_resume import ParseResumeInput, ParseResumeUseCase
from app.application.use_cases.resume.upload_resume import UploadResumeInput, UploadResumeUseCase
from app.domain.entities.resume import Resume, WorkExperience
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, UnauthorizedError


def _make_resume(user_id: uuid.UUID | None = None) -> Resume:
    uid = user_id or uuid.uuid4()
    return Resume(
        id=uuid.uuid4(),
        user_id=uid,
        file_url="https://r2.example.com/resume.pdf",
        file_name="resume.pdf",
        raw_text="",
        skills=["Python", "FastAPI"],
    )


# ── Upload ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_upload_resume_stores_file_and_creates_record() -> None:
    user_id = uuid.uuid4()
    resume = _make_resume(user_id)

    repo = MagicMock()
    repo.create = AsyncMock(return_value=resume)

    storage = MagicMock()
    storage.upload = AsyncMock(return_value="https://r2.example.com/resumes/resume.pdf")

    use_case = UploadResumeUseCase(resume_repo=repo, storage=storage)
    result = await use_case.execute(
        UploadResumeInput(
            user_id=user_id,
            file_bytes=b"PDF content here",
            filename="resume.pdf",
            content_type="application/pdf",
        )
    )

    assert result.resume.user_id == user_id
    storage.upload.assert_called_once()
    repo.create.assert_called_once()
    assert "resumes/" in result.storage_key


# ── Parse ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_parse_resume_calls_agent_and_updates_repo() -> None:
    user_id = uuid.uuid4()
    resume = _make_resume(user_id)
    parsed_resume = _make_resume(user_id)
    parsed_resume.skills = ["Python", "FastAPI", "PostgreSQL", "Redis"]
    parsed_resume.experience = [
        WorkExperience(
            id=uuid.uuid4(),
            company="Acme",
            role="Engineer",
            start_date="2023-01",
            end_date="2025-01",
        )
    ]

    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=resume)
    repo.update = AsyncMock(return_value=parsed_resume)

    parser = MagicMock()
    parser.parse = AsyncMock(return_value=parsed_resume)

    use_case = ParseResumeUseCase(resume_repo=repo, parser=parser)
    result = await use_case.execute(
        ParseResumeInput(
            resume_id=resume.id,
            user_id=user_id,
            raw_text="John Doe, Python Developer...",
        )
    )

    parser.parse.assert_called_once()
    repo.update.assert_called_once()
    assert len(result.skills) == 4


@pytest.mark.asyncio
async def test_parse_resume_wrong_user_raises() -> None:
    owner_id = uuid.uuid4()
    attacker_id = uuid.uuid4()
    resume = _make_resume(owner_id)

    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=resume)

    parser = MagicMock()

    use_case = ParseResumeUseCase(resume_repo=repo, parser=parser)

    with pytest.raises(UnauthorizedError):
        await use_case.execute(
            ParseResumeInput(
                resume_id=resume.id,
                user_id=attacker_id,
                raw_text="raw text",
            )
        )


@pytest.mark.asyncio
async def test_parse_resume_not_found_raises() -> None:
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=None)
    parser = MagicMock()

    use_case = ParseResumeUseCase(resume_repo=repo, parser=parser)

    with pytest.raises(EntityNotFoundError):
        await use_case.execute(
            ParseResumeInput(
                resume_id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                raw_text="raw text",
            )
        )


# ── Get ───────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_resume_returns_correct_resume() -> None:
    user_id = uuid.uuid4()
    resume = _make_resume(user_id)

    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=resume)

    use_case = GetResumeUseCase(repo)
    result = await use_case.execute(resume_id=resume.id, user_id=user_id)

    assert result.id == resume.id


@pytest.mark.asyncio
async def test_get_resume_wrong_user_raises() -> None:
    resume = _make_resume()

    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=resume)

    use_case = GetResumeUseCase(repo)

    with pytest.raises(UnauthorizedError):
        await use_case.execute(resume_id=resume.id, user_id=uuid.uuid4())


@pytest.mark.asyncio
async def test_get_resume_not_found_raises() -> None:
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=None)

    use_case = GetResumeUseCase(repo)

    with pytest.raises(EntityNotFoundError):
        await use_case.execute(resume_id=uuid.uuid4(), user_id=uuid.uuid4())


# ── List ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_resume_versions_returns_all_user_resumes() -> None:
    user_id = uuid.uuid4()
    resumes = [_make_resume(user_id), _make_resume(user_id), _make_resume(user_id)]

    repo = MagicMock()
    repo.get_by_user_id = AsyncMock(return_value=resumes)

    use_case = ListResumeVersionsUseCase(repo)
    result = await use_case.execute(user_id)

    assert len(result) == 3
    assert all(r.user_id == user_id for r in result)

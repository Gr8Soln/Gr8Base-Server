"""Unit tests for Career Profile Engine use cases."""

import uuid
from unittest.mock import AsyncMock, Mock

import pytest

from app.application.use_cases.career.get_profile import GetCareerProfileUseCase
from app.application.use_cases.career.ingest_resume import (
    IngestResumeInput,
    IngestResumeUseCase,
)
from app.application.use_cases.career.update_profile import (
    UpdateCareerProfileInput,
    UpdateCareerProfileUseCase,
)
from app.domain.entities.career_profile import CareerProfile
from app.domain.enums.ingestion_status import IngestionStatus
from app.domain.exceptions.domain_exceptions import EntityNotFoundError


class TestUpdateCareerProfileUseCase:
    @pytest.mark.asyncio
    async def test_update_existing_profile(self, sample_career_profile):
        mock_repo = AsyncMock()
        mock_repo.get_by_user_id.return_value = sample_career_profile
        mock_repo.update.return_value = sample_career_profile

        uc = UpdateCareerProfileUseCase(mock_repo)
        result = await uc.execute(UpdateCareerProfileInput(
            user_id=sample_career_profile.user_id,
            headline="Staff Engineer",
        ))

        assert result.headline == "Staff Engineer"
        mock_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_nonexistent_profile(self, sample_user_id):
        mock_repo = AsyncMock()
        mock_repo.get_by_user_id.return_value = None

        uc = UpdateCareerProfileUseCase(mock_repo)
        with pytest.raises(EntityNotFoundError):
            await uc.execute(UpdateCareerProfileInput(user_id=sample_user_id))


class TestGetCareerProfileUseCase:
    @pytest.mark.asyncio
    async def test_get_full_profile(self, sample_career_profile):
        mock_profile_repo = AsyncMock()
        mock_profile_repo.get_by_user_id.return_value = sample_career_profile

        def make_repo(return_val=None):
            r = AsyncMock()
            r.get_by_user_id.return_value = return_val or []
            return r

        uc = GetCareerProfileUseCase(
            profile_repo=mock_profile_repo,
            experience_repo=make_repo(),
            project_repo=make_repo(),
            skill_repo=make_repo(),
            tech_repo=make_repo(),
            education_repo=make_repo(),
            cert_repo=make_repo(),
            award_repo=make_repo(),
            pub_repo=make_repo(),
            blog_repo=make_repo(),
            lang_repo=make_repo(),
        )
        result = await uc.execute(sample_career_profile.user_id)
        assert result.profile.full_name == "Jane Doe"

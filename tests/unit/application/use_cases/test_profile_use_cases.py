import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.use_cases.profile.get_profile import GetProfileUseCase
from app.application.use_cases.profile.update_profile import (
    UpdateProfileInput,
    UpdateProfileUseCase,
)
from app.domain.entities.user import CareerProfile
from app.domain.exceptions.domain_exceptions import EntityNotFoundError


def _make_profile(user_id: uuid.UUID | None = None) -> CareerProfile:
    return CareerProfile(
        id=uuid.uuid4(),
        user_id=user_id or uuid.uuid4(),
        full_name="Emmanuel",
        email="emmanuel@example.com",
    )


@pytest.mark.asyncio
async def test_get_profile_returns_profile() -> None:
    profile = _make_profile()
    repo = MagicMock()
    repo.get_by_user_id = AsyncMock(return_value=profile)

    use_case = GetProfileUseCase(repo)
    result = await use_case.execute(profile.user_id)

    assert result.user_id == profile.user_id
    assert result.email == "emmanuel@example.com"


@pytest.mark.asyncio
async def test_get_profile_not_found_raises() -> None:
    repo = MagicMock()
    repo.get_by_user_id = AsyncMock(return_value=None)

    use_case = GetProfileUseCase(repo)

    with pytest.raises(EntityNotFoundError):
        await use_case.execute(uuid.uuid4())


@pytest.mark.asyncio
async def test_update_profile_partial_update() -> None:
    user_id = uuid.uuid4()
    profile = _make_profile(user_id)
    updated = CareerProfile(
        id=profile.id,
        user_id=user_id,
        full_name="Emmanuel Updated",
        email="emmanuel@example.com",
        headline="Senior Backend Engineer",
    )

    repo = MagicMock()
    repo.get_by_user_id = AsyncMock(return_value=profile)
    repo.update = AsyncMock(return_value=updated)

    use_case = UpdateProfileUseCase(repo)
    result = await use_case.execute(UpdateProfileInput(
        user_id=user_id,
        full_name="Emmanuel Updated",
        headline="Senior Backend Engineer",
    ))

    assert result.full_name == "Emmanuel Updated"
    assert result.headline == "Senior Backend Engineer"
    repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_profile_not_found_raises() -> None:
    repo = MagicMock()
    repo.get_by_user_id = AsyncMock(return_value=None)

    use_case = UpdateProfileUseCase(repo)

    with pytest.raises(EntityNotFoundError):
        await use_case.execute(UpdateProfileInput(user_id=uuid.uuid4(), full_name="X"))

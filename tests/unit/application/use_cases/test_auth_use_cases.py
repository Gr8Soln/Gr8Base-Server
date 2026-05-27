import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.use_cases.auth.authenticate_user import (
    AuthenticateUserInput,
    AuthenticateUserUseCase,
)
from app.application.use_cases.auth.refresh_token import RefreshTokenUseCase
from app.application.use_cases.auth.register_user import RegisterUserInput, RegisterUserUseCase
from app.domain.entities.user import CareerProfile, User
from app.domain.exceptions.domain_exceptions import DuplicateEntityError, UnauthorizedError
from app.infrastructure.security.password_handler import hash_password


def _make_user(email: str = "test@example.com") -> User:
    return User(
        id=uuid.uuid4(),
        email=email,
        hashed_password=hash_password("password123"),
        full_name="Test User",
        is_active=True,
        is_verified=False,
    )


def _make_profile(user: User) -> CareerProfile:
    return CareerProfile(
        id=uuid.uuid4(),
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
    )


# ── Register ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_user_success() -> None:
    user = _make_user()
    profile = _make_profile(user)

    user_repo = MagicMock()
    user_repo.get_by_email = AsyncMock(return_value=None)
    user_repo.create = AsyncMock(return_value=user)

    profile_repo = MagicMock()
    profile_repo.create = AsyncMock(return_value=profile)

    use_case = RegisterUserUseCase(user_repo, profile_repo)
    result = await use_case.execute(RegisterUserInput(
        email="test@example.com",
        password="password123",
        full_name="Test User",
    ))

    assert result.user.email == "test@example.com"
    assert result.profile.user_id == user.id
    user_repo.create.assert_called_once()
    profile_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_register_duplicate_email_raises() -> None:
    user_repo = MagicMock()
    user_repo.get_by_email = AsyncMock(return_value=_make_user())

    profile_repo = MagicMock()

    use_case = RegisterUserUseCase(user_repo, profile_repo)

    with pytest.raises(DuplicateEntityError):
        await use_case.execute(RegisterUserInput(
            email="test@example.com",
            password="password123",
            full_name="Test User",
        ))


# ── Authenticate ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_authenticate_user_success() -> None:
    user = _make_user()
    user_repo = MagicMock()
    user_repo.get_by_email = AsyncMock(return_value=user)

    use_case = AuthenticateUserUseCase(user_repo)
    result = await use_case.execute(AuthenticateUserInput(
        email="test@example.com",
        password="password123",
    ))

    assert result.access_token
    assert result.refresh_token
    assert result.token_type == "bearer"


@pytest.mark.asyncio
async def test_authenticate_wrong_password_raises() -> None:
    user = _make_user()
    user_repo = MagicMock()
    user_repo.get_by_email = AsyncMock(return_value=user)

    use_case = AuthenticateUserUseCase(user_repo)

    with pytest.raises(UnauthorizedError):
        await use_case.execute(AuthenticateUserInput(
            email="test@example.com",
            password="wrongpassword",
        ))


@pytest.mark.asyncio
async def test_authenticate_unknown_email_raises() -> None:
    user_repo = MagicMock()
    user_repo.get_by_email = AsyncMock(return_value=None)

    use_case = AuthenticateUserUseCase(user_repo)

    with pytest.raises(UnauthorizedError):
        await use_case.execute(AuthenticateUserInput(
            email="nobody@example.com",
            password="password123",
        ))


@pytest.mark.asyncio
async def test_authenticate_inactive_user_raises() -> None:
    user = _make_user()
    user.is_active = False

    user_repo = MagicMock()
    user_repo.get_by_email = AsyncMock(return_value=user)

    use_case = AuthenticateUserUseCase(user_repo)

    with pytest.raises(UnauthorizedError):
        await use_case.execute(AuthenticateUserInput(
            email="test@example.com",
            password="password123",
        ))


# ── Refresh Token ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_refresh_token_invalid_raises() -> None:
    user_repo = MagicMock()
    user_repo.get_by_id = AsyncMock(return_value=None)

    use_case = RefreshTokenUseCase(user_repo)

    with pytest.raises(UnauthorizedError):
        await use_case.execute("not.a.valid.jwt")

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.api.dependencies.auth import get_current_user
from app.adapters.api.schemas.auth_schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserResponse,
)
from app.adapters.persistence.repositories.pg_user_repository import (
    PgCareerProfileRepository,
    PgUserRepository,
)
from app.application.use_cases.auth.authenticate_user import (
    AuthenticateUserInput,
    AuthenticateUserUseCase,
)
from app.application.use_cases.auth.refresh_token import RefreshTokenUseCase
from app.application.use_cases.auth.register_user import RegisterUserInput, RegisterUserUseCase
from app.domain.entities.user import User
from app.infrastructure.database.connection import get_db_session

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    session: AsyncSession = Depends(get_db_session),
) -> RegisterResponse:
    use_case = RegisterUserUseCase(
        user_repo=PgUserRepository(session),
        profile_repo=PgCareerProfileRepository(session),
    )
    result = await use_case.execute(RegisterUserInput(
        email=body.email,
        password=body.password,
        full_name=body.full_name,
    ))
    return RegisterResponse(
        user=UserResponse(
            id=str(result.user.id),
            email=result.user.email,
            full_name=result.user.full_name,
            is_active=result.user.is_active,
            is_verified=result.user.is_verified,
        ),
        access_token=_make_token(result.user),
        refresh_token=_make_refresh(result.user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    use_case = AuthenticateUserUseCase(user_repo=PgUserRepository(session))
    result = await use_case.execute(AuthenticateUserInput(
        email=body.email,
        password=body.password,
    ))
    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    session: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    use_case = RefreshTokenUseCase(user_repo=PgUserRepository(session))
    result = await use_case.execute(body.refresh_token)
    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
    )


# ── helpers (avoid importing jwt_handler twice in routes) ────────────────────
def _make_token(user: User) -> str:
    from app.infrastructure.security.jwt_handler import create_access_token
    return create_access_token(str(user.id))


def _make_refresh(user: User) -> str:
    from app.infrastructure.security.jwt_handler import create_refresh_token
    return create_refresh_token(str(user.id))






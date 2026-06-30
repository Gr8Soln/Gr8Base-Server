from fastapi import Depends

from app.application.interfaces import (
    AccountRepository,
    AuthService,
)

from app.application.use_cases import (
    LoginUseCase,
    RefreshTokenUseCase,
)
from app.presentation.api.dependencies.core_dep import (
    get_account_repository,
    get_jwt_service,
)


def get_login_usecase(
    account_repo: AccountRepository = Depends(get_account_repository),
    jwt_srv: AuthService = Depends(get_jwt_service),
) -> LoginUseCase:
    return LoginUseCase(account_repo, jwt_srv)


def get_refresh_token_usecase(
    account_repo: AccountRepository = Depends(get_account_repository),
    jwt_srv: AuthService = Depends(get_jwt_service),
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(account_repo, jwt_srv)

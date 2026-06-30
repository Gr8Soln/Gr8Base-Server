from fastapi import APIRouter, Depends, status
from starlette.responses import JSONResponse

from app.application.use_cases import (ConfirmEmailUseCase,
                                       ForgotPasswordUseCase, LoginUseCase,
                                       RefreshTokenUseCase, RegisterUseCase,
                                       ResendConfirmEmailUseCase,
                                       ResetPasswordUseCase)
from app.core.exceptions import (AccountAlreadyExistsError,
                                 AccountInactiveError, AccountNotFoundError,
                                 EmailNotVerifiedError, InvalidCredentialError,
                                 InvalidTokenError)
from app.core.utils import error_response, success_response
from app.presentation.api.dependencies import (
    get_login_usecase, get_refresh_token_usecase)
from app.presentation.api.schemas import (AccountResponse, LoginRequest, 
                                         TokenResponse)
from app.core.logging import get_logger
from typing import Optional

logger = get_logger()

auth_router = APIRouter(prefix="/auth", tags=["Auth Endpoints"])


def _error_response(message: str, status_code: int, e: Optional[Exception] = None) -> JSONResponse:
    if e:
        logger.error(str(e), exc_info=e)

    response = error_response(message)
    return JSONResponse(
        content=response.model_dump(mode="json"),
        status_code=status_code,
    )

def _account_response(account) -> AccountResponse:
    return AccountResponse(
        id=account.id,
        email=account.email,
        first_name=account.first_name,
        last_name=account.last_name,
        avatar_url=account.avatar_url,
        status=account.status,
        created_at=account.created_at,
        updated_at=account.updated_at,
    )


def _auth_response(account, tokens, message: str):
    return success_response(
        data={
            "account": _account_response(account).model_dump(mode="json"),
            "tokens": TokenResponse(
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
            ).model_dump(mode="json"),
        },
        message=message,
    )


@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    body: LoginRequest,
    use_case: LoginUseCase = Depends(get_login_usecase),
):
    try:
        account, tokens = await use_case.execute(body.email, body.password)
        return _auth_response(account, tokens, "Login successful")
    
    except InvalidCredentialError as exc:
        return _error_response(str(exc), status.HTTP_401_UNAUTHORIZED)
    except EmailNotVerifiedError as exc:
        return _error_response(str(exc), status.HTTP_403_FORBIDDEN)
    except AccountInactiveError as exc:
        return _error_response(str(exc), status.HTTP_403_FORBIDDEN)
    except Exception as exc:
        return _error_json(
            "An error occurred while logging in",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            exc
        )


@auth_router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_token(
    body: RefreshTokenRequest,
    use_case: RefreshTokenUseCase = Depends(get_refresh_token_usecase),
):
    try:
        tokens = await use_case.execute(body.refresh_token)
        return success_response(
            data=TokenResponse(
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
            ).model_dump(mode="json"),
            message="Token refreshed",
        )
    except (InvalidCredentialError, AccountNotFoundError) as exc:
        return _error_json(str(exc), status.HTTP_401_UNAUTHORIZED)
    except AccountInactiveError as exc:
        return _error_json(str(exc), status.HTTP_403_FORBIDDEN)
    except Exception as exc:
        return _error_json(
            "An error occurred while refreshing token",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            exc
        )

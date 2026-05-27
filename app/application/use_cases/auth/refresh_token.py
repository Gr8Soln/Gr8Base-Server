import uuid
from dataclasses import dataclass

from jose import JWTError

from app.application.ports.repositories.user_repository import UserRepository
from app.domain.exceptions.domain_exceptions import UnauthorizedError
from app.infrastructure.security.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
)


@dataclass
class RefreshTokenOutput:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenUseCase:
    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, refresh_token: str) -> RefreshTokenOutput:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise UnauthorizedError("Invalid token type")
            user_id = uuid.UUID(payload["sub"])
        except (JWTError, KeyError, ValueError):
            raise UnauthorizedError("Invalid or expired refresh token")

        user = await self._user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedError("User not found or inactive")

        return RefreshTokenOutput(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

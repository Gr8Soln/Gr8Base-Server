from dataclasses import dataclass

from app.application.ports.repositories.user_repository import UserRepository
from app.domain.entities.user import User
from app.domain.exceptions.domain_exceptions import UnauthorizedError
from app.infrastructure.security.jwt_handler import create_access_token, create_refresh_token
from app.infrastructure.security.password_handler import verify_password


@dataclass
class AuthenticateUserInput:
    email: str
    password: str


@dataclass
class AuthenticateUserOutput:
    user: User
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthenticateUserUseCase:
    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, data: AuthenticateUserInput) -> AuthenticateUserOutput:
        user = await self._user_repo.get_by_email(data.email.lower())

        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedError("Account is deactivated")

        return AuthenticateUserOutput(
            user=user,
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )







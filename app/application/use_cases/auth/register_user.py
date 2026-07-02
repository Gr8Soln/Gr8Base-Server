from dataclasses import dataclass

from app.application.ports.repositories.user_repository import (
    CareerProfileRepository,
    UserRepository,
)
from app.domain.entities.user import CareerProfile, User
from app.domain.exceptions.domain_exceptions import DuplicateEntityError
from app.infrastructure.security.password_handler import hash_password


@dataclass
class RegisterUserInput:
    email: str
    password: str
    full_name: str


@dataclass
class RegisterUserOutput:
    user: User
    profile: CareerProfile


class RegisterUserUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        profile_repo: CareerProfileRepository,
    ) -> None:
        self._user_repo = user_repo
        self._profile_repo = profile_repo

    async def execute(self, data: RegisterUserInput) -> RegisterUserOutput:
        existing = await self._user_repo.get_by_email(data.email.lower())
        if existing:
            raise DuplicateEntityError("User", "email")

        user = User(
            email=data.email.lower(),
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            is_active=True,
            is_verified=False,
        )
        user = await self._user_repo.create(user)

        profile = CareerProfile(
            user_id=user.id,
            full_name=user.full_name,
            email=user.email,
        )
        profile = await self._profile_repo.create(profile)

        return RegisterUserOutput(user=user, profile=profile)

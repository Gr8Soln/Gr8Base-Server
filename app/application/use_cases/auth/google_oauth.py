import httpx
from fastapi import HTTPException
from google.auth.transport import requests
from google.oauth2 import id_token

from app.application.ports.repositories.user_repository import UserRepository
from app.application.use_cases.auth.authenticate_user import AuthenticateUserOutput
from app.domain.entities.user import User
from app.infrastructure.security.jwt_handler import create_access_token, create_refresh_token


class GoogleAuthUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        google_client_id: str
    ) -> None:
        self._user_repo = user_repo
        self._google_client_id = google_client_id


    async def execute(self, code: str, is_access_token: bool | None = True) -> tuple[User, dict, bool]:
        google_user = {}
        if is_access_token:
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(
                        "https://www.googleapis.com/oauth2/v3/userinfo",
                        headers={"Authorization": f"Bearer {code}"}
                    )
                    if resp.status_code != 200:
                        raise HTTPException(status_code=401, detail="Invalid token")
                    google_user = resp.json()
            except ValueError:
                raise HTTPException(status_code=401, detail="An error occured, try again!")
        else:
            try:
                google_user = id_token.verify_oauth2_token(
                    code,
                    requests.Request(),
                    self._google_client_id,
                    clock_skew_in_seconds=10
                )
            except ValueError:
                raise HTTPException(status_code=401, detail="Invalid token")

        email = google_user["email"]
        first_name = google_user.get("name", "").split(" ")[0]
        last_name = google_user.get("family_name", "")
        google_sub = google_user["sub"]
        avatar = google_user.get("picture")

        user = await self._user_repo.get_by_email(email)
        if not user:
            user = User.create_google_user(
                email=email,
                full_name=f"{first_name} {last_name}".strip(),
                google_sub=google_sub,
                avatar_url=avatar,
            )
            user = await self._user_repo.create(user)

        return AuthenticateUserOutput(
            user=user,
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

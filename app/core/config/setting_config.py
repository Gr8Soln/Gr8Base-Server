from decimal import Decimal
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_PORT: int = 9001
    APP_NAME: str = "Gr8Base"
    APP_ENV: str = "development"
    LOG_DIR: str = "logs"
    DEBUG: bool = False
    CORS_ALLOW_ORIGINS: list[str] = ["*"]
    API_PREFIX: str = "/api/v1"
    WEBHOOK_PREFIX: str = "/webhook/v1"

    # LINKS/URLS
    DASHBOARD_URL: str
    SERVER_URL: str 

    # DB & CACHE
    DATABASE_URL: str
    REDIS_URL: str

    # RATE LIMITING
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # EMAIL
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    SUPPORT_EMAIL: str
    EMAIL_TIMEOUT_SECONDS: int = 15
    EMAIL_USE_SSL: bool = True
    EMAIL_USE_TLS: bool = False

    # JWT
    JWT_SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_TTL: int = 7 * 24 * 60 * 60  # 7 days
    JWT_REFRESH_TOKEN_TTL: int = 30 * 24 * 60 * 60  # 30 days

    # OTP
    OTP_CODE_LENGTH: int = 6
    OTP_VERIFICATION_TTL_SECONDS: int = 60 * 60
    OTP_PASSWORD_RESET_TTL_SECONDS: int = 60 * 60

    # STORAGE
    R2_ENDPOINT_URL: str
    R2_ACCESS_KEY_ID: str
    R2_SECRET_ACCESS_KEY: str
    R2_BUCKET_NAME: str
    R2_BUCKET_URL: str

    # CELERY
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"


    # AI INFRA
    EMBEDDER: str = 'openai'   # openai | local
    VECTOR_DB: str = 'qdrant'   # qdrant | pgvector


    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("DEBUG", mode="before")
    @classmethod
    def _parse_debug(cls, v):
        if isinstance(v, bool) or v is None:
            return v
        if isinstance(v, (int, float)):
            return bool(v)
        if isinstance(v, str):
            s = v.strip().lower()
            if s in {"1", "true", "t", "yes", "y", "on", "debug"}:
                return True
            if s in {"0", "false", "f", "no", "n", "off", "release", "prod", "production"}:
                return False
        # Fall back to False instead of failing hard on unexpected values.
        return False


@lru_cache
def get_settings() -> Settings:
    return Settings()

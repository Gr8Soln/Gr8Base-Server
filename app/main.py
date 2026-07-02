from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.api.middleware.error_middleware import domain_exception_handler
from app.adapters.api.routes import (
    ats_routes,
    auth_routes,
    job_routes,
    profile_routes,
    resume_routes,
)
from app.adapters.api.schemas.common_schemas import HealthResponse
from app.domain.exceptions.domain_exceptions import DomainException
from app.infrastructure.config.settings import settings
from app.infrastructure.observability.structlog_setup import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    if settings.sentry_dsn:
        from app.infrastructure.observability.sentry_setup import setup_sentry
        setup_sentry()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.is_development else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_exception_handler(DomainException, domain_exception_handler)  # type: ignore[arg-type]

    api_prefix = "/api/v1"
    app.include_router(auth_routes.router, prefix=f"{api_prefix}/auth", tags=["Auth"])
    app.include_router(profile_routes.router, prefix=f"{api_prefix}/profile", tags=["Profile"])
    app.include_router(resume_routes.router, prefix=f"{api_prefix}/resumes", tags=["Resumes"])
    app.include_router(job_routes.router, prefix=f"{api_prefix}/jobs", tags=["Jobs"])
    app.include_router(ats_routes.router, prefix=f"{api_prefix}/ats", tags=["ATS"])

    @app.get("/health", response_model=HealthResponse, tags=["System"])
    async def health_check() -> HealthResponse:
        return HealthResponse(
            status="ok",
            version=settings.app_version,
            environment=str(settings.app_env),
        )

    return app


app = create_app()

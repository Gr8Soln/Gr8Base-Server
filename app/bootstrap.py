from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging import logger
from app.core.utils import error_response, success_response
from app.infrastructure.services.redis_cache_service import RedisCacheService


settings = get_settings()

# Lifespan
@asynccontextmanager
async def lifespan(_: FastAPI):
    """Startup / shutdown lifecycle hook."""
    logger.info(f"🟢 {settings.APP_NAME} App started")
    yield
    logger.info(f"🔴 {settings.APP_NAME} App stopped")


def create_app() -> FastAPI:
    """Build and return a fully-configured FastAPI application."""

    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        lifespan=lifespan,
        docs_url=f"{settings.API_PREFIX}/docs",
        redoc_url=f"{settings.API_PREFIX}/redoc",
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
    )

    # Middleware 
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        RateLimitMiddleware,
        cache_service=RedisCacheService(settings.REDIS_URL),
        settings=settings,
    )

    # Exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        errors = exc.errors()
        error_messages = []
        for error in errors:
            field = " -> ".join(
                str(loc) for loc in error["loc"] if loc != "body"
            )
            message = error["msg"]
            error_messages.append(f"{field}: {message}")

        detail = "; ".join(
            error_messages) if error_messages else "Validation error"
        response = error_response(detail)
        return JSONResponse(status_code=422, content=jsonable_encoder(response))

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        response = error_response(exc.detail)
        return JSONResponse(
            status_code=exc.status_code, content=jsonable_encoder(response)
        )

    @app.exception_handler(PermissionError)
    async def permission_exception_handler(request: Request, exc: PermissionError):
        response = error_response(str(exc))
        return JSONResponse(
            status_code=403, content=jsonable_encoder(response)
        )

        return JSONResponse(status_code=500, content=jsonable_encoder(response))


    # Api Routes
    # app.include_router(auth_router, prefix=settings.API_PREFIX)
  
    # Webhook Routes
    # app.include_router(webhook_router, prefix=settings.WEBHOOK_PREFIX)


    @app.get(f"{settings.API_PREFIX}/health")
    async def health():
        return success_response(
            "API is healthy",
            data={
                "status": "healthy",
                "version": "1.0.0",
                "app_name": settings.APP_NAME,
                "debug": settings.DEBUG
            }
        )

    return app

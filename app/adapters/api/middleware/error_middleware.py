from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.domain.exceptions.domain_exceptions import (
    AIGenerationError,
    DuplicateEntityError,
    EntityNotFoundError,
    FileProcessingError,
    StorageError,
    UnauthorizedError,
    ValidationError,
    WorkflowError,
)
from app.infrastructure.observability.structlog_setup import get_logger

logger = get_logger(__name__)


async def domain_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, EntityNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "not_found", "message": str(exc)},
        )

    if isinstance(exc, UnauthorizedError):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": "forbidden", "message": str(exc)},
        )

    if isinstance(exc, (ValidationError, DuplicateEntityError)):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": "validation_error", "message": str(exc)},
        )

    if isinstance(exc, (WorkflowError, AIGenerationError)):
        logger.error("workflow_error", error=str(exc), path=str(request.url))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "processing_error", "message": str(exc)},
        )

    if isinstance(exc, FileProcessingError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": "file_processing_error", "message": str(exc)},
        )

    if isinstance(exc, StorageError):
        logger.error("storage_error", error=str(exc))
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"error": "storage_error", "message": "File storage unavailable"},
        )

    logger.error("unhandled_exception", error=str(exc), path=str(request.url))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "internal_error", "message": "An unexpected error occurred"},
    )

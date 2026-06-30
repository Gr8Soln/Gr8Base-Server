import hashlib
import math
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

from app.presentation.schemas import (Pagination, ResponseModel,
                                          ResponseStatus)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)

def new_uuid(return_str: bool = False) -> str | UUID:
    uuid = uuid4()
    return str(uuid) if return_str else uuid


# =====- Http Response Functions -=========================

def create_response(
    status: ResponseStatus, 
    message: str, 
    data: Optional[Any] = None, 
    metadata: Optional[Pagination] = None
) -> ResponseModel[Any]:
    return ResponseModel(
        status=status, 
        message=message, 
        data=data, 
        metadata=metadata
    )

def success_response(
    message: str,
    data: Optional[Any] = None,
    metadata: Optional[Pagination] = None
) -> ResponseModel[Any]:
    """Create a standardized success response."""
    return ResponseModel(
        status=ResponseStatus.SUCCESS.value, 
        message=message, 
        data=data, 
        metadata=metadata
    )

def error_response(
    message: str,
    data: Optional[Any] = None
) -> ResponseModel[Any]:
    """Create a standardized error response."""
    return ResponseModel(
        status=ResponseStatus.FAILED.value, 
        message=message, 
        data=data
    )

# =====- Pagination Functions -=========================
    
def generate_pagination(
    current_page: int, 
    page_size: int, 
    total_data: int, 
    total_fetched: int
) -> Pagination:
    total_pages = math.ceil(total_data / page_size)

    return Pagination(
        current_page=current_page,
        page_size=page_size,
        total_data=total_data,
        total_data_fetched=total_fetched,
        total_pages=total_pages,
        previous_page=current_page - 1 if current_page > 1 else None,
        next_page=current_page + 1 if current_page < total_pages else None,
    )



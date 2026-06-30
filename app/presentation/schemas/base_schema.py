from enum import Enum
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

# Generic type variable for response data
T = TypeVar("T")

class Pagination(BaseModel):
    current_page: int
    page_size: int
    total_data: int
    total_data_fetched: int
    total_pages: Optional[int] = None
    previous_page: Optional[int] = None
    next_page: Optional[int] = None

class ResponseStatus(str, Enum):
    SUCCESSFUL = "successfull"
    FAILED = "failed"

class ResponseModel(BaseModel, Generic[T]):
    """Generic response model that accepts a type parameter for the data field."""
    status: ResponseStatus
    message: str
    data: Optional[T] = None
    metadata: Optional[Pagination] = None

    class Config:
        from_attributes = True
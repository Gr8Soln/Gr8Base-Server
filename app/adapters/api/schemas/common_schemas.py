from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    environment: str


class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool


class ErrorResponse(BaseModel):
    error: str
    message: str
    detail: str | None = None

class DomainException(Exception):  # noqa: N818
    """Base domain exception."""

    pass


class EntityNotFoundError(DomainException):
    def __init__(self, entity: str, entity_id: str) -> None:
        super().__init__(f"{entity} with id '{entity_id}' not found")
        self.entity = entity
        self.entity_id = entity_id


class UnauthorizedError(DomainException):
    def __init__(self, message: str = "Not authorized") -> None:
        super().__init__(message)


class ValidationError(DomainException):
    def __init__(self, field: str, message: str) -> None:
        super().__init__(f"Validation error on '{field}': {message}")
        self.field = field


class DuplicateEntityError(DomainException):
    def __init__(self, entity: str, field: str) -> None:
        super().__init__(f"{entity} with this {field} already exists")


class WorkflowError(DomainException):
    def __init__(self, workflow: str, message: str) -> None:
        super().__init__(f"Workflow '{workflow}' failed: {message}")
        self.workflow = workflow


class AIGenerationError(DomainException):
    def __init__(self, agent: str, message: str) -> None:
        super().__init__(f"Agent '{agent}' failed: {message}")
        self.agent = agent


class FileProcessingError(DomainException):
    def __init__(self, filename: str, message: str) -> None:
        super().__init__(f"Failed to process '{filename}': {message}")
        self.filename = filename


class StorageError(DomainException):
    def __init__(self, message: str) -> None:
        super().__init__(f"Storage error: {message}")

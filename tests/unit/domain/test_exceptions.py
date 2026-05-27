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


def test_entity_not_found_error() -> None:
    err = EntityNotFoundError("Resume", "abc-123")
    assert "Resume" in str(err)
    assert "abc-123" in str(err)
    assert err.entity == "Resume"
    assert err.entity_id == "abc-123"


def test_unauthorized_error_default_message() -> None:
    err = UnauthorizedError()
    assert "Not authorized" in str(err)


def test_validation_error() -> None:
    err = ValidationError("email", "invalid format")
    assert "email" in str(err)
    assert "invalid format" in str(err)


def test_duplicate_entity_error() -> None:
    err = DuplicateEntityError("User", "email")
    assert "User" in str(err)
    assert "email" in str(err)


def test_workflow_error() -> None:
    err = WorkflowError("resume_optimization", "node failed")
    assert err.workflow == "resume_optimization"
    assert "node failed" in str(err)


def test_ai_generation_error() -> None:
    err = AIGenerationError("resume_parser_agent", "LLM timeout")
    assert err.agent == "resume_parser_agent"


def test_file_processing_error() -> None:
    err = FileProcessingError("resume.pdf", "corrupted file")
    assert err.filename == "resume.pdf"


def test_storage_error() -> None:
    err = StorageError("R2 bucket unreachable")
    assert "R2 bucket" in str(err)


def test_exceptions_are_domain_exceptions() -> None:
    from app.domain.exceptions.domain_exceptions import DomainException

    assert isinstance(EntityNotFoundError("X", "1"), DomainException)
    assert isinstance(UnauthorizedError(), DomainException)
    assert isinstance(WorkflowError("w", "m"), DomainException)

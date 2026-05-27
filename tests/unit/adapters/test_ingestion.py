import pytest

from app.adapters.ingestion.ingestion_router import extract_text
from app.adapters.ingestion.txt_extractor import extract_text_from_txt
from app.domain.exceptions.domain_exceptions import FileProcessingError


def test_txt_extractor_returns_text() -> None:
    content = b"John Doe\nSenior Backend Engineer\n5 years experience"
    result = extract_text_from_txt(content, "resume.txt")
    assert "John Doe" in result
    assert "Backend Engineer" in result


def test_txt_extractor_empty_raises() -> None:
    with pytest.raises(FileProcessingError) as exc_info:
        extract_text_from_txt(b"   ", "empty.txt")
    assert "empty" in str(exc_info.value).lower()


def test_ingestion_router_unsupported_type_raises() -> None:
    with pytest.raises(FileProcessingError) as exc_info:
        extract_text(b"data", "image/png", "photo.png")
    assert "Unsupported" in str(exc_info.value)


def test_ingestion_router_file_too_large_raises() -> None:
    big_file = b"x" * (11 * 1024 * 1024)  # 11MB
    with pytest.raises(FileProcessingError) as exc_info:
        extract_text(big_file, "text/plain", "huge.txt")
    assert "10MB" in str(exc_info.value)


def test_ingestion_router_dispatches_txt() -> None:
    content = b"Backend Engineer with Python and FastAPI"
    result = extract_text(content, "text/plain", "resume.txt")
    assert "Backend Engineer" in result


def test_ingestion_router_dispatches_pdf() -> None:
    # Can't test real PDF without a file — test that wrong bytes raise properly
    with pytest.raises(FileProcessingError):
        extract_text(b"not a real pdf", "application/pdf", "bad.pdf")

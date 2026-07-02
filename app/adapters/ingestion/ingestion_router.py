from app.adapters.ingestion.docx_extractor import extract_text_from_docx
from app.adapters.ingestion.pdf_extractor import extract_text_from_pdf
from app.adapters.ingestion.txt_extractor import extract_text_from_txt
from app.domain.exceptions.domain_exceptions import FileProcessingError

SUPPORTED_TYPES = {
    "application/pdf": extract_text_from_pdf,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": extract_text_from_docx,  # noqa: E501
    "text/plain": extract_text_from_txt,
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def extract_text(file_bytes: bytes, content_type: str, filename: str) -> str:
    if len(file_bytes) > MAX_FILE_SIZE:
        raise FileProcessingError(filename, "File exceeds 10MB limit")

    extractor = SUPPORTED_TYPES.get(content_type)
    if not extractor:
        raise FileProcessingError(
            filename,
            f"Unsupported file type '{content_type}'. Supported: PDF, DOCX, TXT",
        )

    return extractor(file_bytes, filename)

import io

from docx import Document

from app.domain.exceptions.domain_exceptions import FileProcessingError


def extract_text_from_docx(file_bytes: bytes, filename: str = "file.docx") -> str:
    try:
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        raw = "\n\n".join(paragraphs)

        if not raw.strip():
            raise FileProcessingError(filename, "No extractable text found in DOCX")

        return raw
    except FileProcessingError:
        raise
    except Exception as e:
        raise FileProcessingError(filename, f"DOCX extraction failed: {e}") from e

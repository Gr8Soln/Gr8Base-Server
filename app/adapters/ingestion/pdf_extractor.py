import io

import pdfplumber

from app.domain.exceptions.domain_exceptions import FileProcessingError


def extract_text_from_pdf(file_bytes: bytes, filename: str = "file.pdf") -> str:
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = []
            for page in pdf.pages:
                text = page.extract_text(x_tolerance=2, y_tolerance=2)
                if text:
                    pages.append(text.strip())
            raw = "\n\n".join(pages)

        if not raw.strip():
            raise FileProcessingError(filename, "No extractable text found — may be a scanned PDF")

        return raw
    except FileProcessingError:
        raise
    except Exception as e:
        raise FileProcessingError(filename, f"PDF extraction failed: {e}") from e

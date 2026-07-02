from app.domain.exceptions.domain_exceptions import FileProcessingError


def extract_text_from_txt(file_bytes: bytes, filename: str = "file.txt") -> str:
    try:
        raw = file_bytes.decode("utf-8", errors="replace").strip()
        if not raw:
            raise FileProcessingError(filename, "Text file is empty")
        return raw
    except FileProcessingError:
        raise
    except Exception as e:
        raise FileProcessingError(filename, f"TXT extraction failed: {e}") from e

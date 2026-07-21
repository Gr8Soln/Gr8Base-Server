from enum import StrEnum


class IngestionStatus(StrEnum):
    PENDING = "pending"
    EXTRACTING = "extracting"
    PARSING = "parsing"
    ENRICHING = "enriching"
    EMBEDDING = "embedding"
    COMPLETED = "completed"
    FAILED = "failed"

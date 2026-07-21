from dataclasses import dataclass

from app.application.ports.events.event_bus_port import DomainEvent


@dataclass
class ResumeUploaded(DomainEvent):
    user_id: str = ""
    file_name: str = ""
    file_url: str = ""
    event_type: str = "resume.uploaded"


@dataclass
class ResumeParsingStarted(DomainEvent):
    user_id: str = ""
    resume_id: str = ""
    event_type: str = "resume.parsing_started"


@dataclass
class ResumeParsed(DomainEvent):
    user_id: str = ""
    resume_id: str = ""
    skills_count: int = 0
    experiences_count: int = 0
    event_type: str = "resume.parsed"


@dataclass
class CareerProfileCreated(DomainEvent):
    user_id: str = ""
    event_type: str = "career_profile.created"


@dataclass
class CareerProfileUpdated(DomainEvent):
    user_id: str = ""
    updated_fields: list[str] | None = None
    event_type: str = "career_profile.updated"


@dataclass
class EnrichmentStarted(DomainEvent):
    user_id: str = ""
    companies_count: int = 0
    event_type: str = "enrichment.started"


@dataclass
class EnrichmentCompleted(DomainEvent):
    user_id: str = ""
    enriched_companies: list[str] | None = None
    event_type: str = "enrichment.completed"


@dataclass
class EmbeddingsGenerated(DomainEvent):
    user_id: str = ""
    embeddings_count: int = 0
    entity_types: list[str] | None = None
    event_type: str = "embeddings.generated"


@dataclass
class ResumeIngestionCompleted(DomainEvent):
    user_id: str = ""
    workflow_id: str = ""
    duration_ms: int = 0
    event_type: str = "ingestion.completed"


@dataclass
class ResumeIngestionFailed(DomainEvent):
    user_id: str = ""
    workflow_id: str = ""
    error_message: str = ""
    event_type: str = "ingestion.failed"

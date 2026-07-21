from app.adapters.persistence.models.ingestion_model import IngestionWorkflowModel
from app.application.ports.repositories.ingestion_repository import IngestionWorkflow
from app.domain.enums.ingestion_status import IngestionStatus


class IngestionMapper:
    @staticmethod
    def to_entity(model: IngestionWorkflowModel) -> IngestionWorkflow:
        return IngestionWorkflow(
            id=model.id,
            user_id=model.user_id,
            status=IngestionStatus(model.status),
            source_file_key=model.source_file_key,
            source_file_name=model.source_file_name,
            source_file_url=model.source_file_url,
            error_message=model.error_message,
            events=model.events or [],
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: IngestionWorkflow) -> IngestionWorkflowModel:
        return IngestionWorkflowModel(
            id=entity.id,
            user_id=entity.user_id,
            status=entity.status.value,
            source_file_key=entity.source_file_key,
            source_file_name=entity.source_file_name,
            source_file_url=entity.source_file_url,
            error_message=entity.error_message,
            events=entity.events,
        )

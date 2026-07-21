from app.adapters.ai.workflows.resume_ingestion.nodes import (
    enrich_data_node,
    extract_text_node,
    generate_embeddings_node,
    parse_career_node,
    persist_profile_node,
)
from app.application.ports.repositories.ingestion_repository import IngestionWorkflow
from app.domain.enums.ingestion_status import IngestionStatus
from app.infrastructure.observability.structlog_setup import get_logger

logger = get_logger(__name__)


async def run_ingestion_pipeline(
    state: dict,
    session,
    ingestion_repo,
    workflow: IngestionWorkflow,
) -> dict:
    """Run the complete resume ingestion pipeline.

    Args:
        state: Initial state dict with user_id, file_bytes, filename, content_type
        session: SQLAlchemy AsyncSession
        ingestion_repo: IngestionRepository instance
        workflow: IngestionWorkflow tracking entity

    Returns:
        Final state dict with status and extracted data
    """
    logger.info("ingestion_pipeline_start", workflow_id=str(workflow.id))

    # Node 1: Extract text
    await ingestion_repo.update_status(workflow.id, IngestionStatus.EXTRACTING)
    await ingestion_repo.append_event(workflow.id, "extracting_started", {})
    state.update(await extract_text_node(state))
    if state.get("status") == "failed":
        await ingestion_repo.update_status(
            workflow.id, IngestionStatus.FAILED, "; ".join(state.get("errors", []))
        )
        await ingestion_repo.append_event(
            workflow.id, "extracting_failed", {"errors": state.get("errors", [])}
        )
        return state
    await ingestion_repo.append_event(workflow.id, "extracting_completed", {})

    # Node 2: Parse career data
    await ingestion_repo.update_status(workflow.id, IngestionStatus.PARSING)
    await ingestion_repo.append_event(workflow.id, "parsing_started", {})
    state.update(await parse_career_node(state))
    if state.get("status") == "failed":
        await ingestion_repo.update_status(
            workflow.id, IngestionStatus.FAILED, "; ".join(state.get("errors", []))
        )
        await ingestion_repo.append_event(
            workflow.id, "parsing_failed", {"errors": state.get("errors", [])}
        )
        return state
    await ingestion_repo.append_event(
        workflow.id,
        "parsing_completed",
        {
            "experiences": len(state.get("extracted_experiences", [])),
            "skills": len(state.get("extracted_skills", [])),
        },
    )

    # Node 3: Enrich data
    await ingestion_repo.update_status(workflow.id, IngestionStatus.ENRICHING)
    await ingestion_repo.append_event(workflow.id, "enriching_started", {})
    state.update(await enrich_data_node(state))
    await ingestion_repo.append_event(workflow.id, "enriching_completed", {})

    # Node 4: Generate embeddings
    await ingestion_repo.update_status(workflow.id, IngestionStatus.EMBEDDING)
    await ingestion_repo.append_event(workflow.id, "embedding_started", {})
    state.update(await generate_embeddings_node(state))
    await ingestion_repo.append_event(workflow.id, "embedding_completed", {})

    # Node 5: Persist to database
    state.update(await persist_profile_node(state, session))
    if state.get("status") == "failed":
        await ingestion_repo.update_status(
            workflow.id, IngestionStatus.FAILED, "; ".join(state.get("errors", []))
        )
        return state

    await ingestion_repo.update_status(workflow.id, IngestionStatus.COMPLETED)
    await ingestion_repo.append_event(
        workflow.id,
        "ingestion_completed",
        {
            "status": "completed",
        },
    )
    logger.info("ingestion_pipeline_complete", workflow_id=str(workflow.id))
    return state

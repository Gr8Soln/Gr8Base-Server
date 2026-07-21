from app.infrastructure.config.normalizer import normalize_database_url
from app.infrastructure.observability.structlog_setup import get_logger
from app.infrastructure.queue.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(
    name="ingestion_tasks.run_ingestion_pipeline",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue="default",
)
def run_ingestion_pipeline_task(
    self,
    workflow_id: str,
    user_id: str,
    file_bytes: bytes,
    filename: str,
    content_type: str,
) -> dict:
    """Async task: runs the full resume ingestion pipeline after file upload."""
    import asyncio
    import uuid

    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.adapters.ai.workflows.resume_ingestion.workflow import run_ingestion_pipeline
    from app.adapters.persistence.repositories.pg_ingestion_repository import PgIngestionRepository
    from app.infrastructure.config.settings import get_settings

    settings = get_settings()

    async def _run() -> dict:
        engine = create_async_engine(normalize_database_url(settings.database_url), echo=False)
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        async with session_factory() as session:
            async with session.begin():
                ingestion_repo = PgIngestionRepository(session)
                wf = await ingestion_repo.get_by_id(uuid.UUID(workflow_id))
                if not wf:
                    return {"error": "Workflow not found", "workflow_id": workflow_id}

                state = {
                    "user_id": user_id,
                    "workflow_id": workflow_id,
                    "file_bytes": file_bytes,
                    "filename": filename,
                    "content_type": content_type,
                }
                result = await run_ingestion_pipeline(
                    state=state,
                    session=session,
                    ingestion_repo=ingestion_repo,
                    workflow=wf,
                )

        await engine.dispose()
        return {
            "workflow_id": workflow_id,
            "status": result.get("status", "unknown"),
        }

    try:
        result = asyncio.run(_run())
        logger.info(
            "ingestion_pipeline_task_done",
            workflow_id=workflow_id,
            status=result.get("status"),
        )
        return result
    except Exception as exc:
        logger.error(
            "ingestion_pipeline_task_failed",
            workflow_id=workflow_id,
            error=str(exc),
        )
        raise self.retry(exc=exc)

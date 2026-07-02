from app.infrastructure.config.normalizer import normalize_database_url
from app.infrastructure.observability.structlog_setup import get_logger
from app.infrastructure.queue.celery_app import celery_app
from app.infrastructure.config.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()

@celery_app.task(
    name="embedding_tasks.generate_resume_embedding",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    queue="embedding",
)
def generate_resume_embedding_task(
    self, resume_id: str, raw_text: str, skills: list[str]
) -> dict:
    """Generates and stores embedding for a resume after parsing completes."""
    import asyncio

    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.infrastructure.vector.embedding_service import generate_resume_embedding


    async def _run() -> dict:
        embedding = await generate_resume_embedding(raw_text, skills)
        embedding_str = "[" + ",".join(str(v) for v in embedding) + "]"

        engine = create_async_engine(normalize_database_url(settings.database_url), echo=False)
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        async with session_factory() as session:
            async with session.begin():
                await session.execute(
                    text(
                        "UPDATE resumes SET embedding = :emb::vector "
                        "WHERE id = :id"
                    ),
                    {"emb": embedding_str, "id": resume_id},
                )

        await engine.dispose()
        logger.info("resume_embedding_stored", resume_id=resume_id)
        return {"resume_id": resume_id, "dimensions": len(embedding), "status": "indexed"}

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("resume_embedding_task_failed", resume_id=resume_id, error=str(exc))
        raise self.retry(exc=exc)


@celery_app.task(
    name="embedding_tasks.generate_job_embedding",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    queue="embedding",
)
def generate_job_embedding_task(
    self, job_id: str, raw_text: str, required_skills: list[str]
) -> dict:
    """Generates and stores embedding for a job description after analysis."""
    import asyncio

    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.infrastructure.config.settings import get_settings
    from app.infrastructure.vector.embedding_service import generate_job_embedding

    async def _run() -> dict:
        embedding = await generate_job_embedding(raw_text, required_skills)
        embedding_str = "[" + ",".join(str(v) for v in embedding) + "]"

        engine = create_async_engine(normalize_database_url(settings.database_url), echo=False)
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        async with session_factory() as session:
            async with session.begin():
                await session.execute(
                    text(
                        "UPDATE jobs SET embedding = :emb::vector "
                        "WHERE id = :id"
                    ),
                    {"emb": embedding_str, "id": job_id},
                )

        await engine.dispose()
        logger.info("job_embedding_stored", job_id=job_id)
        return {"job_id": job_id, "dimensions": len(embedding), "status": "indexed"}

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("job_embedding_task_failed", job_id=job_id, error=str(exc))
        raise self.retry(exc=exc)

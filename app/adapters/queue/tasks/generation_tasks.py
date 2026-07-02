from app.infrastructure.observability.structlog_setup import get_logger
from app.infrastructure.queue.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(
    name="generation_tasks.optimize_resume",
    bind=True,
    max_retries=2,
    default_retry_delay=60,
    queue="generation",
    time_limit=300,  # 5 min hard limit
    soft_time_limit=240,
)
def optimize_resume_task(
    self, resume_id: str, job_id: str, user_id: str, strategy: str, label: str
) -> dict:
    """Runs the full resume optimization workflow asynchronously."""
    import asyncio
    import uuid

    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.adapters.persistence.repositories.pg_job_repository import PgJobRepository
    from app.adapters.persistence.repositories.pg_resume_repository import PgResumeRepository
    from app.adapters.queue.tasks.embedding_tasks import generate_resume_embedding_task
    from app.application.use_cases.resume.optimize_resume import (
        OptimizeResumeInput,
        OptimizeResumeUseCase,
    )
    from app.domain.enums.resume_strategy import ResumeStrategy
    from app.infrastructure.config.settings import settings

    async def _run() -> dict:
        engine = create_async_engine(settings.database_url, echo=False)
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        async with session_factory() as session:
            async with session.begin():
                use_case = OptimizeResumeUseCase(
                    resume_repo=PgResumeRepository(session),
                    job_repo=PgJobRepository(session),
                )
                optimized = await use_case.execute(
                    OptimizeResumeInput(
                        resume_id=uuid.UUID(resume_id),
                        job_id=uuid.UUID(job_id),
                        user_id=uuid.UUID(user_id),
                        strategy=ResumeStrategy(strategy),
                        label=label,
                    )
                )

        await engine.dispose()
        return {
            "optimized_resume_id": str(optimized.id),
            "ats_score_snapshot": optimized.ats_score_snapshot,
            "version": optimized.version,
            "label": optimized.label,
        }

    try:
        result = asyncio.run(_run())
        # Chain: generate embedding for optimized resume
        generate_resume_embedding_task.delay(
            resume_id=result["optimized_resume_id"],
            raw_text="",
            skills=result.get("skills", []),
        )
        return result
    except Exception as exc:
        logger.error("optimize_resume_task_failed", resume_id=resume_id, error=str(exc))
        raise self.retry(exc=exc)

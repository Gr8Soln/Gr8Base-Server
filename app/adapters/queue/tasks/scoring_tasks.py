from app.infrastructure.observability.structlog_setup import get_logger
from app.infrastructure.queue.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(
    name="scoring_tasks.score_resume",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue="scoring",
)
def score_resume_task(self, resume_id: str, job_id: str, user_id: str) -> dict:
    """Runs the full ATS scoring workflow asynchronously."""
    import asyncio
    import uuid

    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.adapters.persistence.repositories.pg_ats_repository import PgATSRepository
    from app.adapters.persistence.repositories.pg_job_repository import PgJobRepository
    from app.adapters.persistence.repositories.pg_resume_repository import PgResumeRepository
    from app.application.use_cases.ats.score_resume import ScoreResumeInput, ScoreResumeUseCase
    from app.infrastructure.config.settings import settings

    async def _run() -> dict:
        engine = create_async_engine(settings.database_url, echo=False)
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        async with session_factory() as session:
            async with session.begin():
                use_case = ScoreResumeUseCase(
                    ats_repo=PgATSRepository(session),
                    resume_repo=PgResumeRepository(session),
                    job_repo=PgJobRepository(session),
                )
                score = await use_case.execute(
                    ScoreResumeInput(
                        resume_id=uuid.UUID(resume_id),
                        job_id=uuid.UUID(job_id),
                        user_id=uuid.UUID(user_id),
                    )
                )

        await engine.dispose()
        return {
            "score_id": str(score.id),
            "resume_id": resume_id,
            "job_id": job_id,
            "overall_score": score.overall_score,
            "status": "scored",
        }

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("score_resume_task_failed", resume_id=resume_id, error=str(exc))
        raise self.retry(exc=exc)

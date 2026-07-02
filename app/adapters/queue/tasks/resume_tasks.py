from app.infrastructure.config.normalizer import normalize_database_url
from app.infrastructure.observability.structlog_setup import get_logger
from app.infrastructure.queue.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(
    name="resume_tasks.parse_resume",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    queue="resume",
)
def parse_resume_task(self, resume_id: str, user_id: str, raw_text: str) -> dict:
    """
    Async task: runs the resume parsing pipeline after file upload.
    On success, chains to embedding generation automatically.
    """
    import asyncio
    import uuid

    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.adapters.ai.agents.resume_parser_agent import ResumeParserAgent
    from app.adapters.persistence.repositories.pg_resume_repository import PgResumeRepository
    from app.adapters.queue.tasks.embedding_tasks import generate_resume_embedding_task
    from app.application.use_cases.resume.parse_resume import ParseResumeInput, ParseResumeUseCase
    from app.infrastructure.config.settings import get_settings

    settings = get_settings()

    async def _run() -> dict:
        engine = create_async_engine(normalize_database_url(settings.database_url), echo=False)
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        async with session_factory() as session:
            async with session.begin():
                use_case = ParseResumeUseCase(
                    resume_repo=PgResumeRepository(session),
                    parser=ResumeParserAgent(),
                )
                resume = await use_case.execute(
                    ParseResumeInput(
                        resume_id=uuid.UUID(resume_id),
                        user_id=uuid.UUID(user_id),
                        raw_text=raw_text,
                    )
                )

        await engine.dispose()
        return {
            "resume_id": resume_id,
            "skills": resume.skills,
            "raw_text": raw_text,
        }

    try:
        result = asyncio.run(_run())
        # Chain: after parsing completes, generate embedding
        generate_resume_embedding_task.delay(
            resume_id=resume_id,
            raw_text=result["raw_text"],
            skills=result["skills"],
        )
        return {
            "resume_id": resume_id,
            "skills_count": len(result["skills"]),
            "status": "parsed",
            "embedding": "queued",
        }
    except Exception as exc:
        logger.error("parse_resume_task_failed", resume_id=resume_id, error=str(exc))
        raise self.retry(exc=exc)

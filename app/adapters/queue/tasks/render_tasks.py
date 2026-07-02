from app.infrastructure.observability.structlog_setup import get_logger
from app.infrastructure.queue.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(
    name="render_tasks.generate_pdf",
    bind=True,
    max_retries=2,
    default_retry_delay=30,
    queue="rendering",
    time_limit=120,
)
def generate_pdf_task(self, resume_id: str, user_id: str, template: str = "classic") -> dict:
    """Renders resume to PDF and stores in R2. Returns signed download URL."""
    import asyncio
    import uuid

    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.adapters.persistence.repositories.pg_resume_repository import PgResumeRepository
    from app.adapters.renderer.pdf_renderer import WeasyPrintPDFRenderer
    from app.adapters.storage.r2_file_storage import R2FileStorage
    from app.application.use_cases.resume.generate_resume_pdf import (
        GeneratePDFInput,
        GenerateResumePDFUseCase,
    )
    from app.infrastructure.config.settings import settings

    async def _run() -> dict:
        engine = create_async_engine(settings.database_url, echo=False)
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        storage = R2FileStorage()

        async with session_factory() as session:
            repo = PgResumeRepository(session)
            renderer = WeasyPrintPDFRenderer(resume_repo=repo, storage=storage)
            use_case = GenerateResumePDFUseCase(resume_repo=repo, renderer=renderer)
            result = await use_case.execute(
                GeneratePDFInput(
                    resume_id=uuid.UUID(resume_id),
                    user_id=uuid.UUID(user_id),
                    template=template,
                )
            )

        signed_url = await storage.get_signed_url(
            key=f"pdfs/{user_id}/{resume_id}_{template}.pdf"
        )
        await engine.dispose()

        return {
            "resume_id": resume_id,
            "pdf_url": result.pdf_url,
            "download_url": signed_url,
            "template": template,
            "status": "rendered",
        }

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("generate_pdf_task_failed", resume_id=resume_id, error=str(exc))
        raise self.retry(exc=exc)

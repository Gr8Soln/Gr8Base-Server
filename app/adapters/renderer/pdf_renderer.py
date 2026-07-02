import uuid

from app.adapters.renderer.html_renderer import render_resume_html
from app.application.ports.renderer.pdf_renderer_port import PDFRendererPort
from app.application.ports.repositories.resume_repository import ResumeRepository
from app.application.ports.storage.file_storage_port import FileStoragePort
from app.domain.exceptions.domain_exceptions import EntityNotFoundError
from app.infrastructure.observability.structlog_setup import get_logger

logger = get_logger(__name__)


class WeasyPrintPDFRenderer(PDFRendererPort):
    def __init__(
        self,
        resume_repo: ResumeRepository,
        storage: FileStoragePort,
    ) -> None:
        self._resume_repo = resume_repo
        self._storage = storage

    async def render(self, resume_id: uuid.UUID, template: str = "classic") -> str:
        from weasyprint import HTML

        resume = await self._resume_repo.get_by_id(resume_id)
        if not resume:
            raise EntityNotFoundError("Resume", str(resume_id))

        html_content = render_resume_html(resume, template_name=template)

        logger.info("pdf_render_start", resume_id=str(resume_id), template=template)

        pdf_bytes = HTML(string=html_content).write_pdf()

        storage_key = f"pdfs/{resume.user_id}/{resume_id}_{template}.pdf"
        pdf_url = await self._storage.upload(
            file_bytes=pdf_bytes,
            key=storage_key,
            content_type="application/pdf",
        )

        logger.info(
            "pdf_render_complete",
            resume_id=str(resume_id),
            size_kb=round(len(pdf_bytes) / 1024, 1),
        )
        return pdf_url

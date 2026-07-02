import uuid
from dataclasses import dataclass

from app.application.ports.renderer.pdf_renderer_port import PDFRendererPort
from app.application.ports.repositories.resume_repository import ResumeRepository
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, UnauthorizedError


@dataclass
class GeneratePDFInput:
    resume_id: uuid.UUID
    user_id: uuid.UUID
    template: str = "classic"


@dataclass
class GeneratePDFOutput:
    resume_id: uuid.UUID
    pdf_url: str
    template: str


class GenerateResumePDFUseCase:
    def __init__(
        self,
        resume_repo: ResumeRepository,
        renderer: PDFRendererPort,
    ) -> None:
        self._resume_repo = resume_repo
        self._renderer = renderer

    async def execute(self, data: GeneratePDFInput) -> GeneratePDFOutput:
        resume = await self._resume_repo.get_by_id(data.resume_id)
        if not resume:
            raise EntityNotFoundError("Resume", str(data.resume_id))
        if resume.user_id != data.user_id:
            raise UnauthorizedError("Resume does not belong to this user")

        pdf_url = await self._renderer.render(
            resume_id=data.resume_id,
            template=data.template,
        )
        return GeneratePDFOutput(
            resume_id=data.resume_id,
            pdf_url=pdf_url,
            template=data.template,
        )

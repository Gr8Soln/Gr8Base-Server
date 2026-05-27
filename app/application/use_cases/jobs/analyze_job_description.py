import uuid
from dataclasses import dataclass

from app.application.ports.ai.jd_analyzer_port import JDAnalyzerPort
from app.application.ports.repositories.job_repository import JobRepository
from app.domain.entities.job import JobDescription


@dataclass
class AnalyzeJobInput:
    user_id: uuid.UUID
    raw_text: str
    company: str = ""
    company_url: str = ""


class AnalyzeJobDescriptionUseCase:
    def __init__(
        self,
        job_repo: JobRepository,
        analyzer: JDAnalyzerPort,
    ) -> None:
        self._job_repo = job_repo
        self._analyzer = analyzer

    async def execute(self, data: AnalyzeJobInput) -> JobDescription:
        job = JobDescription(
            user_id=data.user_id,
            raw_text=data.raw_text,
            company=data.company,
            company_url=data.company_url,
        )
        job = await self._job_repo.create(job)
        job = await self._analyzer.analyze(data.raw_text, job)
        job = await self._job_repo.update(job)
        return job

from abc import ABC, abstractmethod

from app.domain.entities.job import JobDescription


class JDAnalyzerPort(ABC):
    @abstractmethod
    async def analyze(self, raw_text: str, job: JobDescription) -> JobDescription:
        """
        Analyzes raw JD text and returns a fully structured JobDescription entity.
        """
        ...

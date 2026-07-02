import uuid
from dataclasses import dataclass

from app.application.ports.ai.resume_parser_port import ResumeParserPort
from app.application.ports.repositories.resume_repository import ResumeRepository
from app.domain.entities.resume import Resume
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, UnauthorizedError


@dataclass
class ParseResumeInput:
    resume_id: uuid.UUID
    user_id: uuid.UUID
    raw_text: str


class ParseResumeUseCase:
    def __init__(
        self,
        resume_repo: ResumeRepository,
        parser: ResumeParserPort,
    ) -> None:
        self._resume_repo = resume_repo
        self._parser = parser

    async def execute(self, data: ParseResumeInput) -> Resume:
        resume = await self._resume_repo.get_by_id(data.resume_id)
        if not resume:
            raise EntityNotFoundError("Resume", str(data.resume_id))
        if resume.user_id != data.user_id:
            raise UnauthorizedError("Resume does not belong to this user")

        resume.raw_text = data.raw_text
        resume = await self._parser.parse(data.raw_text, resume)
        resume = await self._resume_repo.update(resume)

        return resume

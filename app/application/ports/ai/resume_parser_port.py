from abc import ABC, abstractmethod

from app.domain.entities.resume import Resume


class ResumeParserPort(ABC):
    @abstractmethod
    async def parse(self, raw_text: str, resume: Resume) -> Resume:
        """
        Takes raw extracted text and a Resume entity (with file metadata),
        returns the same Resume with all structured fields populated.
        """
        ...

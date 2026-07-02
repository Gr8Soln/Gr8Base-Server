import uuid
from abc import ABC, abstractmethod


class PDFRendererPort(ABC):
    @abstractmethod
    async def render(self, resume_id: uuid.UUID, template: str = "classic") -> str:
        """
        Renders a resume to PDF. Returns the storage URL of the generated PDF.
        """
        ...

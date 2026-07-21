from abc import ABC, abstractmethod

from app.domain.entities.career_profile import CareerProfile


class CareerExtractorPort(ABC):
    """Abstract port for AI-powered career profile extraction from raw text.

    Extracts all structured career entities from resume/LinkedIn text.
    """

    @abstractmethod
    async def extract(self, raw_text: str, user_id: str, profile: CareerProfile) -> dict:
        """Extract full career profile data from raw resume text.

        Returns a dict with keys: profile, experiences, projects, skills,
        technologies, education, certifications, awards, publications,
        blogs, languages.
        """
        ...

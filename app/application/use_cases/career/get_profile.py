import uuid
from dataclasses import dataclass

from app.application.ports.repositories.career_profile_repository import CareerProfileRepository
from app.application.ports.repositories.education_repository import EducationRepository
from app.application.ports.repositories.experience_repository import ExperienceRepository
from app.application.ports.repositories.project_repository import ProjectRepository
from app.application.ports.repositories.skill_repository import SkillRepository
from app.application.ports.repositories.certification_repository import CertificationRepository
from app.application.ports.repositories.award_repository import AwardRepository
from app.application.ports.repositories.language_repository import LanguageRepository
from app.application.ports.repositories.technology_repository import TechnologyRepository
from app.application.ports.repositories.publication_repository import PublicationRepository
from app.application.ports.repositories.blog_repository import BlogRepository
from app.domain.entities.career_profile import CareerProfile
from app.domain.exceptions.domain_exceptions import EntityNotFoundError


@dataclass
class CareerProfileFull:
    profile: CareerProfile
    experiences: list
    projects: list
    skills: list
    technologies: list
    education: list
    certifications: list
    awards: list
    publications: list
    blogs: list
    languages: list


class GetCareerProfileUseCase:
    def __init__(
        self,
        profile_repo: CareerProfileRepository,
        experience_repo: ExperienceRepository,
        project_repo: ProjectRepository,
        skill_repo: SkillRepository,
        tech_repo: TechnologyRepository,
        education_repo: EducationRepository,
        cert_repo: CertificationRepository,
        award_repo: AwardRepository,
        pub_repo: PublicationRepository,
        blog_repo: BlogRepository,
        lang_repo: LanguageRepository,
    ) -> None:
        self._profile_repo = profile_repo
        self._experience_repo = experience_repo
        self._project_repo = project_repo
        self._skill_repo = skill_repo
        self._tech_repo = tech_repo
        self._education_repo = education_repo
        self._cert_repo = cert_repo
        self._award_repo = award_repo
        self._pub_repo = pub_repo
        self._blog_repo = blog_repo
        self._lang_repo = lang_repo

    async def execute(self, user_id: uuid.UUID) -> CareerProfileFull:
        profile = await self._profile_repo.get_by_user_id(user_id)
        if not profile:
            raise EntityNotFoundError("CareerProfile", str(user_id))

        return CareerProfileFull(
            profile=profile,
            experiences=await self._experience_repo.get_by_user_id(user_id),
            projects=await self._project_repo.get_by_user_id(user_id),
            skills=await self._skill_repo.get_by_user_id(user_id),
            technologies=await self._tech_repo.get_by_user_id(user_id),
            education=await self._education_repo.get_by_user_id(user_id),
            certifications=await self._cert_repo.get_by_user_id(user_id),
            awards=await self._award_repo.get_by_user_id(user_id),
            publications=await self._pub_repo.get_by_user_id(user_id),
            blogs=await self._blog_repo.get_by_user_id(user_id),
            languages=await self._lang_repo.get_by_user_id(user_id),
        )

import uuid

from app.adapters.ai.agents.career_extractor_agent import CareerExtractorAgent
from app.adapters.ai.agents.enrichment_agent import EnrichmentAgent
from app.adapters.ai.providers.openai_embedding_provider import OpenAIEmbeddingProvider
from app.adapters.ai.providers.tavily_search_provider import TavilySearchProvider
from app.adapters.ingestion.ingestion_router import extract_text
from app.adapters.persistence.repositories.pg_award_repository import PgAwardRepository
from app.adapters.persistence.repositories.pg_blog_repository import PgBlogRepository
from app.adapters.persistence.repositories.pg_career_profile_repository import (
    PgCareerProfileRepository,
)
from app.adapters.persistence.repositories.pg_certification_repository import (
    PgCertificationRepository,
)
from app.adapters.persistence.repositories.pg_education_repository import PgEducationRepository
from app.adapters.persistence.repositories.pg_experience_repository import PgExperienceRepository
from app.adapters.persistence.repositories.pg_language_repository import PgLanguageRepository
from app.adapters.persistence.repositories.pg_project_repository import PgProjectRepository
from app.adapters.persistence.repositories.pg_publication_repository import (
    PgPublicationRepository,
)
from app.adapters.persistence.repositories.pg_skill_repository import PgSkillRepository
from app.adapters.persistence.repositories.pg_technology_repository import PgTechnologyRepository
from app.domain.entities.award import Award
from app.domain.entities.blog import Blog
from app.domain.entities.career_profile import CareerProfile
from app.domain.entities.certification import Certification
from app.domain.entities.education import Education
from app.domain.entities.experience import WorkExperience
from app.domain.entities.language import Language
from app.domain.entities.project import Project
from app.domain.entities.publication import Publication
from app.domain.entities.skill import Skill
from app.domain.entities.technology import Technology
from app.domain.enums.employment_type import EmploymentType
from app.domain.enums.skill_category import SkillCategory
from app.domain.exceptions.domain_exceptions import DomainException
from app.infrastructure.observability.structlog_setup import get_logger

logger = get_logger(__name__)


async def extract_text_node(state: dict) -> dict:
    """Node 1: Extract raw text from uploaded file bytes."""
    logger.info("ingestion_extract_text_start", filename=state.get("filename"))
    try:
        raw_text = extract_text(
            file_bytes=state["file_bytes"],
            content_type=state.get("content_type", "application/pdf"),
            filename=state.get("filename", "resume"),
        )
        return {"raw_text": raw_text}
    except DomainException as e:
        return {"errors": [str(e)], "status": "failed"}


async def parse_career_node(state: dict) -> dict:
    """Node 2: AI-powered structured extraction of career profile."""
    logger.info("ingestion_parse_career_start", user_id=state.get("user_id"))

    user_id = uuid.UUID(state["user_id"])
    profile = CareerProfile(
        user_id=user_id,
        full_name="",
        email="",
    )

    try:
        extractor = CareerExtractorAgent()
        result = await extractor.extract(
            raw_text=state["raw_text"],
            user_id=state["user_id"],
            profile=profile,
        )
        return {
            "extracted_profile": {
                "full_name": result["profile"].full_name,
                "email": result["profile"].email,
                "phone": result["profile"].phone,
                "location": result["profile"].location,
                "linkedin_url": result["profile"].linkedin_url,
                "github_url": result["profile"].github_url,
                "portfolio_url": result["profile"].portfolio_url,
                "website": result["profile"].website,
                "headline": result["profile"].headline,
                "summary": result["profile"].summary,
                "years_of_experience": result["profile"].years_of_experience,
            },
            "extracted_experiences": result["experiences"],
            "extracted_projects": result["projects"],
            "extracted_skills": result["skills"],
            "extracted_technologies": result["technologies"],
            "extracted_education": result["education"],
            "extracted_certifications": result["certifications"],
            "extracted_awards": result["awards"],
            "extracted_publications": result["publications"],
            "extracted_blogs": result["blogs"],
            "extracted_languages": result["languages"],
        }
    except Exception as e:
        logger.error("ingestion_parse_career_failed", error=str(e))
        return {"errors": [str(e)], "status": "failed"}


async def enrich_data_node(state: dict) -> dict:
    """Node 3: Web search enrichment."""
    logger.info("ingestion_enrich_start")

    companies = list(
        {
            exp.get("company", "")
            for exp in state.get("extracted_experiences", [])
            if exp.get("company")
        }
    )
    technologies = list(
        {
            tech.get("name", "")
            for tech in state.get("extracted_technologies", [])
            if tech.get("name")
        }
    )

    if not companies and not technologies:
        return {}

    try:
        search = TavilySearchProvider()
        enricher = EnrichmentAgent(search)
        company_enrichments = await enricher.enrich_companies(companies)
        tech_enrichments = await enricher.enrich_technologies(technologies)
        return {
            "company_enrichments": {
                k: {
                    "industry": v.industry,
                    "company_size": v.company_size,
                    "products": v.products,
                    "technology_focus": v.technology_focus,
                    "description": v.description,
                }
                for k, v in company_enrichments.items()
            },
            "technology_enrichments": tech_enrichments,
        }
    except Exception as e:
        logger.warning("ingestion_enrich_failed", error=str(e))
        return {}


async def generate_embeddings_node(state: dict) -> dict:
    """Node 4: Generate embeddings for summary, experiences, and projects."""
    logger.info("ingestion_embeddings_start")

    try:
        embedder = OpenAIEmbeddingProvider()
        result: dict = {}

        # Summary embedding
        summary = state.get("extracted_profile", {}).get("summary", "")
        if summary:
            result["summary_embedding"] = await embedder.generate_embedding(summary)

        # Experience embeddings (one per experience)
        experiences = state.get("extracted_experiences", [])
        exp_texts = [
            f"{e.get('role', '')} at {e.get('company', '')}: {e.get('description', '')}"
            for e in experiences
        ]
        if exp_texts:
            result["experience_embeddings"] = await embedder.generate_embeddings(exp_texts)

        # Project embeddings
        projects = state.get("extracted_projects", [])
        proj_texts = [f"{p.get('name', '')}: {p.get('description', '')}" for p in projects]
        if proj_texts:
            result["project_embeddings"] = await embedder.generate_embeddings(proj_texts)

        logger.info(
            "ingestion_embeddings_done",
            summary=bool(summary),
            experiences=len(experiences),
            projects=len(projects),
        )
        return result
    except Exception as e:
        logger.warning("ingestion_embeddings_failed", error=str(e))
        return {}


async def persist_profile_node(state: dict, session) -> dict:
    """Node 5: Persist all extracted data to the database."""
    logger.info("ingestion_persist_start")

    user_id = uuid.UUID(state["user_id"])
    errors: list[str] = []

    try:
        # Profile
        profile_repo = PgCareerProfileRepository(session)
        existing = await profile_repo.get_by_user_id(user_id)
        profile_data = state.get("extracted_profile", {})
        if existing:
            existing.full_name = profile_data.get("full_name", existing.full_name)
            existing.headline = profile_data.get("headline", existing.headline)
            existing.summary = profile_data.get("summary", existing.summary)
            existing.location = profile_data.get("location", existing.location)
            existing.phone = profile_data.get("phone", existing.phone)
            existing.linkedin_url = profile_data.get("linkedin_url", existing.linkedin_url)
            existing.github_url = profile_data.get("github_url", existing.github_url)
            existing.portfolio_url = profile_data.get("portfolio_url", existing.portfolio_url)
            existing.website = profile_data.get("website", existing.website)
            existing.years_of_experience = profile_data.get(
                "years_of_experience", existing.years_of_experience
            )
            existing.summary_embedding = state.get("summary_embedding")
            await profile_repo.update(existing)
        else:
            profile = CareerProfile(
                user_id=user_id,
                full_name=profile_data.get("full_name", ""),
                email=profile_data.get("email", ""),
                headline=profile_data.get("headline", ""),
                summary=profile_data.get("summary", ""),
                location=profile_data.get("location", ""),
                phone=profile_data.get("phone", ""),
                linkedin_url=profile_data.get("linkedin_url", ""),
                github_url=profile_data.get("github_url", ""),
                portfolio_url=profile_data.get("portfolio_url", ""),
                website=profile_data.get("website", ""),
                years_of_experience=profile_data.get("years_of_experience", 0),
                summary_embedding=state.get("summary_embedding"),
            )
            await profile_repo.create(profile)

        # Experiences
        exp_repo = PgExperienceRepository(session)
        await exp_repo.delete_all_for_user(user_id)
        exp_embeddings = state.get("experience_embeddings", [])
        for i, e in enumerate(state.get("extracted_experiences", [])):
            exp = WorkExperience(
                user_id=user_id,
                company=e.get("company", ""),
                role=e.get("role", ""),
                start_date=e.get("start_date", ""),
                end_date=e.get("end_date"),
                is_current=e.get("is_current", False),
                location=e.get("location", ""),
                description=e.get("description", ""),
                employment_type=EmploymentType(e.get("employment_type", "full_time")),
                responsibilities=e.get("responsibilities", []),
                achievements=e.get("achievements", []),
                technologies=e.get("technologies", []),
                embedding=exp_embeddings[i] if i < len(exp_embeddings) else None,
            )
            await exp_repo.create(exp)

        # Projects
        proj_repo = PgProjectRepository(session)
        await proj_repo.delete_all_for_user(user_id)
        proj_embeddings = state.get("project_embeddings", [])
        for i, p in enumerate(state.get("extracted_projects", [])):
            proj = Project(
                user_id=user_id,
                name=p.get("name", ""),
                description=p.get("description", ""),
                role=p.get("role", ""),
                technologies=p.get("technologies", []),
                responsibilities=p.get("responsibilities", []),
                repository=p.get("repository", ""),
                demo_url=p.get("demo_url", ""),
                url=p.get("url", ""),
                duration=p.get("duration", ""),
                impact=p.get("impact", ""),
                embedding=proj_embeddings[i] if i < len(proj_embeddings) else None,
            )
            await proj_repo.create(proj)

        # Skills
        skill_repo = PgSkillRepository(session)
        await skill_repo.delete_all_for_user(user_id)
        for s in state.get("extracted_skills", []):
            skill = Skill(
                user_id=user_id,
                name=s.get("name", ""),
                category=SkillCategory(s.get("category", "technical")),
                proficiency=s.get("proficiency", ""),
                years_of_experience=s.get("years_of_experience", 0.0),
            )
            await skill_repo.create(skill)

        # Technologies
        tech_repo = PgTechnologyRepository(session)
        await tech_repo.delete_all_for_user(user_id)
        for t in state.get("extracted_technologies", []):
            tech = Technology(
                user_id=user_id,
                name=t.get("name", ""),
                category=SkillCategory(t.get("category", "tool")),
                proficiency=t.get("proficiency", ""),
            )
            await tech_repo.create(tech)

        # Education
        edu_repo = PgEducationRepository(session)
        await edu_repo.delete_all_for_user(user_id)
        for e in state.get("extracted_education", []):
            edu = Education(
                user_id=user_id,
                institution=e.get("institution", ""),
                degree=e.get("degree", ""),
                field_of_study=e.get("field_of_study", ""),
                start_year=e.get("start_year"),
                end_year=e.get("end_year"),
                gpa=e.get("gpa"),
                honors=e.get("honors", ""),
                activities=e.get("activities", ""),
            )
            await edu_repo.create(edu)

        # Certifications
        cert_repo = PgCertificationRepository(session)
        await cert_repo.delete_all_for_user(user_id)
        for c in state.get("extracted_certifications", []):
            cert = Certification(
                user_id=user_id,
                name=c.get("name", ""),
                issuer=c.get("issuer", ""),
                issue_date=c.get("issue_date", ""),
                expiry_date=c.get("expiry_date", ""),
                credential_url=c.get("credential_url", ""),
                credential_id=c.get("credential_id", ""),
            )
            await cert_repo.create(cert)

        # Awards
        award_repo = PgAwardRepository(session)
        await award_repo.delete_all_for_user(user_id)
        for a in state.get("extracted_awards", []):
            award = Award(
                user_id=user_id,
                name=a.get("name", ""),
                issuer=a.get("issuer", ""),
                date=a.get("date", ""),
                description=a.get("description", ""),
            )
            await award_repo.create(award)

        # Publications
        pub_repo = PgPublicationRepository(session)
        await pub_repo.delete_all_for_user(user_id)
        for p in state.get("extracted_publications", []):
            pub = Publication(
                user_id=user_id,
                title=p.get("title", ""),
                publisher=p.get("publisher", ""),
                date=p.get("date", ""),
                url=p.get("url", ""),
                description=p.get("description", ""),
            )
            await pub_repo.create(pub)

        # Blogs
        blog_repo = PgBlogRepository(session)
        await blog_repo.delete_all_for_user(user_id)
        for b in state.get("extracted_blogs", []):
            blog = Blog(
                user_id=user_id,
                title=b.get("title", ""),
                url=b.get("url", ""),
                platform=b.get("platform", ""),
                date=b.get("date", ""),
                description=b.get("description", ""),
            )
            await blog_repo.create(blog)

        # Languages
        lang_repo = PgLanguageRepository(session)
        await lang_repo.delete_all_for_user(user_id)
        for lang in state.get("extracted_languages", []):
            lang = Language(
                user_id=user_id,
                name=lang.get("name", ""),
                proficiency=lang.get("proficiency", ""),
            )
            await lang_repo.create(lang)

        logger.info("ingestion_persist_done", user_id=str(user_id))
        return {"status": "completed"}
    except Exception as e:
        logger.error("ingestion_persist_failed", error=str(e))
        errors.append(str(e))
        return {"errors": errors, "status": "failed"}

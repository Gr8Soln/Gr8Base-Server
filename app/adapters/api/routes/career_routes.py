import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.api.dependencies.auth import get_current_user
from app.adapters.api.schemas.career_schemas import (
    AwardResponse,
    BlogResponse,
    CareerProfileResponse,
    CertificationResponse,
    CreateEntityRequest,
    EducationResponse,
    ExperienceResponse,
    FullCareerProfileResponse,
    ImpactStatementResponse,
    IngestResumeResponse,
    IngestionStatusResponse,
    LanguageResponse,
    ProjectResponse,
    PublicationResponse,
    SkillResponse,
    TechnologyResponse,
    UpdateCareerProfileRequest,
    UpdateEntityRequest,
)
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
from app.adapters.persistence.repositories.pg_ingestion_repository import PgIngestionRepository
from app.adapters.persistence.repositories.pg_language_repository import PgLanguageRepository
from app.adapters.persistence.repositories.pg_project_repository import PgProjectRepository
from app.adapters.persistence.repositories.pg_publication_repository import (
    PgPublicationRepository,
)
from app.adapters.persistence.repositories.pg_skill_repository import PgSkillRepository
from app.adapters.persistence.repositories.pg_technology_repository import PgTechnologyRepository
from app.adapters.storage.r2_file_storage import R2FileStorage
from app.application.use_cases.career.get_profile import GetCareerProfileUseCase
from app.application.use_cases.career.ingest_resume import (
    IngestResumeInput,
    IngestResumeUseCase,
)
from app.application.use_cases.career.manage_entities import (
    CreateEntityInput,
    DeleteEntityInput,
    UpdateEntityInput,
)
from app.application.use_cases.career.update_profile import (
    UpdateCareerProfileInput,
    UpdateCareerProfileUseCase,
)
from app.domain.entities.award import Award
from app.domain.entities.blog import Blog
from app.domain.entities.certification import Certification
from app.domain.entities.education import Education
from app.domain.entities.experience import WorkExperience
from app.domain.entities.language import Language
from app.domain.entities.project import Project
from app.domain.entities.publication import Publication
from app.domain.entities.skill import Skill
from app.domain.entities.technology import Technology
from app.domain.entities.user import User
from app.domain.exceptions.domain_exceptions import EntityNotFoundError
from app.infrastructure.database.connection import get_db_session

router = APIRouter()

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}


# ── Serializers ───────────────────────────────────────────────────────────────


def _profile_response(profile) -> CareerProfileResponse:
    return CareerProfileResponse(
        id=str(profile.id),
        user_id=str(profile.user_id),
        full_name=profile.full_name,
        email=profile.email,
        headline=profile.headline,
        summary=profile.summary,
        location=profile.location,
        phone=profile.phone,
        address=getattr(profile, "address", ""),
        linkedin_url=profile.linkedin_url,
        github_url=profile.github_url,
        portfolio_url=profile.portfolio_url,
        website=getattr(profile, "website", ""),
        years_of_experience=profile.years_of_experience,
        target_roles=profile.target_roles,
        target_industries=profile.target_industries,
        target_salary_min=profile.target_salary_min,
        target_salary_max=profile.target_salary_max,
        preferred_work_type=profile.preferred_work_type,
        writing_tone=profile.writing_tone,
        created_at=str(profile.created_at),
        updated_at=str(profile.updated_at),
    )


# ── Ingestion ─────────────────────────────────────────────────────────────────


@router.post("/ingest", response_model=IngestResumeResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> IngestResumeResponse:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415, detail="Unsupported file type. Allowed: PDF, DOCX, TXT"
        )
    file_bytes = await file.read()
    uc = IngestResumeUseCase(
        storage=R2FileStorage(),
        ingestion_repo=PgIngestionRepository(session),
    )
    result = await uc.execute(
        IngestResumeInput(
            user_id=current_user.id,
            file_bytes=file_bytes,
            filename=file.filename or "resume",
            content_type=file.content_type or "application/pdf",
        )
    )
    # Queue async pipeline task
    from app.adapters.queue.tasks.ingestion_tasks import run_ingestion_pipeline_task

    run_ingestion_pipeline_task.delay(
        workflow_id=str(result.workflow_id),
        user_id=str(current_user.id),
        file_bytes=file_bytes,
        filename=file.filename or "resume",
        content_type=file.content_type or "application/pdf",
    )
    return IngestResumeResponse(
        workflow_id=str(result.workflow_id),
        status=result.status,
        file_url=result.file_url,
    )


@router.get("/ingestion/{workflow_id}", response_model=IngestionStatusResponse)
async def get_ingestion_status(
    workflow_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> IngestionStatusResponse:
    repo = PgIngestionRepository(session)
    wf = await repo.get_by_id(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Ingestion workflow not found")
    return IngestionStatusResponse(
        workflow_id=str(wf.id),
        status=wf.status.value,
        source_file_name=wf.source_file_name,
        error_message=wf.error_message,
        events=wf.events,
        created_at=str(wf.created_at),
        updated_at=str(wf.updated_at),
    )


# ── Profile ───────────────────────────────────────────────────────────────────


@router.get("/profile", response_model=FullCareerProfileResponse)
async def get_career_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> FullCareerProfileResponse:
    uc = GetCareerProfileUseCase(
        profile_repo=PgCareerProfileRepository(session),
        experience_repo=PgExperienceRepository(session),
        project_repo=PgProjectRepository(session),
        skill_repo=PgSkillRepository(session),
        tech_repo=PgTechnologyRepository(session),
        education_repo=PgEducationRepository(session),
        cert_repo=PgCertificationRepository(session),
        award_repo=PgAwardRepository(session),
        pub_repo=PgPublicationRepository(session),
        blog_repo=PgBlogRepository(session),
        lang_repo=PgLanguageRepository(session),
    )
    try:
        full = await uc.execute(current_user.id)
    except EntityNotFoundError:
        raise HTTPException(
            status_code=404, detail="Career profile not found. Upload a resume first."
        )

    return FullCareerProfileResponse(
        profile=_profile_response(full.profile),
        experiences=[
            ExperienceResponse(
                id=str(e.id),
                user_id=str(e.user_id),
                company=e.company,
                role=e.role,
                start_date=e.start_date,
                end_date=e.end_date,
                is_current=e.is_current,
                location=e.location,
                description=e.description,
                employment_type=e.employment_type.value,
                industry=e.industry,
                company_website=e.company_website,
                responsibilities=e.responsibilities,
                achievements=e.achievements,
                technologies=e.technologies,
                impact_statements=[
                    ImpactStatementResponse(
                        problem=i.problem, solution=i.solution, result=i.result, metric=i.metric
                    )
                    for i in e.impact_statements
                ],
                ai_summary=e.ai_summary,
            )
            for e in full.experiences
        ],
        projects=[
            ProjectResponse(
                id=str(p.id),
                user_id=str(p.user_id),
                name=p.name,
                description=p.description,
                role=p.role,
                technologies=p.technologies,
                responsibilities=p.responsibilities,
                repository=p.repository,
                demo_url=p.demo_url,
                url=p.url,
                duration=p.duration,
                impact=p.impact,
                ai_summary=p.ai_summary,
            )
            for p in full.projects
        ],
        skills=[
            SkillResponse(
                id=str(s.id),
                user_id=str(s.user_id),
                name=s.name,
                category=s.category.value,
                proficiency=s.proficiency,
                years_of_experience=s.years_of_experience,
            )
            for s in full.skills
        ],
        technologies=[
            TechnologyResponse(
                id=str(t.id),
                user_id=str(t.user_id),
                name=t.name,
                category=t.category.value,
                proficiency=t.proficiency,
            )
            for t in full.technologies
        ],
        education=[
            EducationResponse(
                id=str(e.id),
                user_id=str(e.user_id),
                institution=e.institution,
                degree=e.degree,
                field_of_study=e.field_of_study,
                start_year=e.start_year,
                end_year=e.end_year,
                gpa=e.gpa,
                honors=e.honors,
                activities=e.activities,
            )
            for e in full.education
        ],
        certifications=[
            CertificationResponse(
                id=str(c.id),
                user_id=str(c.user_id),
                name=c.name,
                issuer=c.issuer,
                issue_date=c.issue_date,
                expiry_date=c.expiry_date,
                credential_url=c.credential_url,
                credential_id=c.credential_id,
            )
            for c in full.certifications
        ],
        awards=[
            AwardResponse(
                id=str(a.id),
                user_id=str(a.user_id),
                name=a.name,
                issuer=a.issuer,
                date=a.date,
                description=a.description,
            )
            for a in full.awards
        ],
        publications=[
            PublicationResponse(
                id=str(p.id),
                user_id=str(p.user_id),
                title=p.title,
                publisher=p.publisher,
                date=p.date,
                url=p.url,
                description=p.description,
            )
            for p in full.publications
        ],
        blogs=[
            BlogResponse(
                id=str(b.id),
                user_id=str(b.user_id),
                title=b.title,
                url=b.url,
                platform=b.platform,
                date=b.date,
                description=b.description,
            )
            for b in full.blogs
        ],
        languages=[
            LanguageResponse(
                id=str(l.id), user_id=str(l.user_id), name=l.name, proficiency=l.proficiency
            )
            for l in full.languages
        ],
    )


@router.patch("/profile", response_model=CareerProfileResponse)
async def update_career_profile(
    body: UpdateCareerProfileRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> CareerProfileResponse:
    uc = UpdateCareerProfileUseCase(PgCareerProfileRepository(session))
    try:
        profile = await uc.execute(
            UpdateCareerProfileInput(
                user_id=current_user.id,
                full_name=body.full_name,
                headline=body.headline,
                summary=body.summary,
                location=body.location,
                phone=body.phone,
                address=body.address,
                linkedin_url=body.linkedin_url,
                github_url=body.github_url,
                portfolio_url=body.portfolio_url,
                website=body.website,
                years_of_experience=body.years_of_experience,
                target_roles=body.target_roles,
                target_industries=body.target_industries,
                preferred_work_type=body.preferred_work_type,
                writing_tone=body.writing_tone,
            )
        )
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Career profile not found")
    return _profile_response(profile)


# ── CRUD: Experiences ─────────────────────────────────────────────────────────


@router.get("/experiences", response_model=list[ExperienceResponse])
async def list_experiences(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[ExperienceResponse]:
    repo = PgExperienceRepository(session)
    exps = await repo.get_by_user_id(current_user.id)
    return [
        ExperienceResponse(
            id=str(e.id),
            user_id=str(e.user_id),
            company=e.company,
            role=e.role,
            start_date=e.start_date,
            end_date=e.end_date,
            is_current=e.is_current,
            location=e.location,
            description=e.description,
            employment_type=e.employment_type.value,
            industry=e.industry,
            company_website=e.company_website,
            responsibilities=e.responsibilities,
            achievements=e.achievements,
            technologies=e.technologies,
            impact_statements=[
                ImpactStatementResponse(
                    problem=i.problem, solution=i.solution, result=i.result, metric=i.metric
                )
                for i in e.impact_statements
            ],
            ai_summary=e.ai_summary,
        )
        for e in exps
    ]


@router.post("/experiences", response_model=ExperienceResponse, status_code=201)
async def create_experience(
    body: CreateEntityRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ExperienceResponse:
    repo = PgExperienceRepository(session)
    exp = WorkExperience(user_id=current_user.id, **body.data)
    result = await repo.create(exp)
    return ExperienceResponse(
        id=str(result.id),
        user_id=str(result.user_id),
        company=result.company,
        role=result.role,
        start_date=result.start_date,
        end_date=result.end_date,
        is_current=result.is_current,
        location=result.location,
        description=result.description,
        employment_type=result.employment_type.value,
        industry=result.industry,
        company_website=result.company_website,
        responsibilities=result.responsibilities,
        achievements=result.achievements,
        technologies=result.technologies,
        impact_statements=[
            ImpactStatementResponse(
                problem=i.problem, solution=i.solution, result=i.result, metric=i.metric
            )
            for i in result.impact_statements
        ],
        ai_summary=result.ai_summary,
    )


@router.patch("/experiences/{experience_id}", response_model=ExperienceResponse)
async def update_experience(
    experience_id: uuid.UUID,
    body: UpdateEntityRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ExperienceResponse:
    repo = PgExperienceRepository(session)
    exp = await repo.get_by_id(experience_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    for key, value in body.data.items():
        if hasattr(exp, key) and value is not None:
            setattr(exp, key, value)
    result = await repo.update(exp)
    return ExperienceResponse(
        id=str(result.id),
        user_id=str(result.user_id),
        company=result.company,
        role=result.role,
        start_date=result.start_date,
        end_date=result.end_date,
        is_current=result.is_current,
        location=result.location,
        description=result.description,
        employment_type=result.employment_type.value,
        industry=result.industry,
        company_website=result.company_website,
        responsibilities=result.responsibilities,
        achievements=result.achievements,
        technologies=result.technologies,
        impact_statements=[
            ImpactStatementResponse(
                problem=i.problem, solution=i.solution, result=i.result, metric=i.metric
            )
            for i in result.impact_statements
        ],
        ai_summary=result.ai_summary,
    )


@router.delete("/experiences/{experience_id}", status_code=204)
async def delete_experience(
    experience_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    repo = PgExperienceRepository(session)
    exp = await repo.get_by_id(experience_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    await repo.delete(experience_id)

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.api.dependencies.auth import get_current_user
from app.adapters.api.schemas.resume_schemas import (
    CertificationResponse,
    EducationResponse,
    ImpactStatementResponse,
    OptimizeResumeRequest,
    OptimizeResumeResponse,
    PDFRenderRequest,
    PDFRenderResponse,
    ProjectResponse,
    ResumeComparisonResponse,
    ResumeResponse,
    ResumeUploadResponse,
    WorkExperienceResponse,
)
from app.adapters.ingestion.ingestion_router import extract_text
from app.adapters.persistence.repositories.pg_resume_repository import PgResumeRepository
from app.adapters.queue.tasks.generation_tasks import optimize_resume_task
from app.adapters.queue.tasks.render_tasks import generate_pdf_task
from app.adapters.queue.tasks.resume_tasks import parse_resume_task
from app.adapters.storage.r2_file_storage import R2FileStorage
from app.application.use_cases.resume.compare_resume_versions import CompareResumeVersionsUseCase
from app.application.use_cases.resume.get_resume import GetResumeUseCase
from app.application.use_cases.resume.list_resume_versions import ListResumeVersionsUseCase
from app.application.use_cases.resume.rollback_resume_version import RollbackResumeVersionUseCase
from app.application.use_cases.resume.upload_resume import UploadResumeInput, UploadResumeUseCase
from app.domain.entities.resume import Resume, WorkExperience
from app.domain.entities.user import User
from app.domain.enums.resume_strategy import ResumeStrategy
from app.infrastructure.database.connection import get_db_session

router = APIRouter()

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}
VALID_TEMPLATES = {"classic", "modern", "minimal"}


# ── Serializers ───────────────────────────────────────────────────────────────

def _serialize_exp(exp: WorkExperience) -> WorkExperienceResponse:
    return WorkExperienceResponse(
        id=str(exp.id),
        company=exp.company,
        role=exp.role,
        start_date=exp.start_date,
        end_date=exp.end_date,
        is_current=exp.is_current,
        location=exp.location,
        description=exp.description,
        technologies=exp.technologies,
        impact_statements=[
            ImpactStatementResponse(
                problem=i.problem, solution=i.solution, result=i.result, metric=i.metric
            )
            for i in exp.impact_statements
        ],
    )


def _resume_response(resume: Resume) -> ResumeResponse:
    return ResumeResponse(
        id=str(resume.id),
        user_id=str(resume.user_id),
        file_name=resume.file_name,
        file_url=resume.file_url,
        version=resume.version,
        label=resume.label,
        strategy=resume.strategy.value if resume.strategy else None,
        ats_score_snapshot=resume.ats_score_snapshot,
        skills=resume.skills,
        experience=[_serialize_exp(e) for e in resume.experience],
        projects=[
            ProjectResponse(
                id=str(p.id), name=p.name, description=p.description,
                technologies=p.technologies, url=p.url, impact=p.impact,
            )
            for p in resume.projects
        ],
        education=[
            EducationResponse(
                id=str(e.id), institution=e.institution, degree=e.degree,
                field_of_study=e.field_of_study, start_year=e.start_year,
                end_year=e.end_year, gpa=e.gpa, honors=e.honors,
            )
            for e in resume.education
        ],
        certifications=[
            CertificationResponse(
                id=str(c.id), name=c.name, issuer=c.issuer,
                issue_date=c.issue_date, expiry_date=c.expiry_date,
                credential_url=c.credential_url,
            )
            for c in resume.certifications
        ],
        languages=resume.languages,
    )


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ResumeUploadResponse:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type. Allowed: PDF, DOCX, TXT",
        )
    file_bytes = await file.read()
    raw_text = extract_text(
        file_bytes=file_bytes,
        content_type=file.content_type or "application/pdf",
        filename=file.filename or "resume",
    )
    upload_uc = UploadResumeUseCase(
        resume_repo=PgResumeRepository(session),
        storage=R2FileStorage(),
    )
    result = await upload_uc.execute(
        UploadResumeInput(
            user_id=current_user.id,
            file_bytes=file_bytes,
            filename=file.filename or "resume",
            content_type=file.content_type or "application/pdf",
        )
    )
    parse_resume_task.delay(
        resume_id=str(result.resume.id),
        user_id=str(current_user.id),
        raw_text=raw_text,
    )
    return ResumeUploadResponse(
        id=str(result.resume.id),
        user_id=str(current_user.id),
        file_name=file.filename or "resume",
    )


@router.get("", response_model=list[ResumeResponse])
async def list_resumes(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[ResumeResponse]:
    uc = ListResumeVersionsUseCase(PgResumeRepository(session))
    return [_resume_response(r) for r in await uc.execute(current_user.id)]


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ResumeResponse:
    uc = GetResumeUseCase(PgResumeRepository(session))
    return _resume_response(await uc.execute(resume_id=resume_id, user_id=current_user.id))


@router.post("/{resume_id}/optimize", response_model=OptimizeResumeResponse,
             status_code=status.HTTP_202_ACCEPTED)
async def optimize_resume(
    resume_id: uuid.UUID,
    body: OptimizeResumeRequest,
    current_user: User = Depends(get_current_user),
) -> OptimizeResumeResponse:
    try:
        strategy = ResumeStrategy(body.strategy)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid strategy. Valid: {[s.value for s in ResumeStrategy]}",
        )
    task = optimize_resume_task.delay(
        resume_id=str(resume_id),
        job_id=body.job_id,
        user_id=str(current_user.id),
        strategy=strategy.value,
        label=body.label,
    )
    return OptimizeResumeResponse(
        task_id=task.id,
        resume_id=str(resume_id),
        job_id=body.job_id,
        strategy=strategy.value,
    )


@router.post("/{resume_id}/pdf", response_model=PDFRenderResponse,
             status_code=status.HTTP_202_ACCEPTED)
async def generate_pdf(
    resume_id: uuid.UUID,
    body: PDFRenderRequest,
    current_user: User = Depends(get_current_user),
) -> PDFRenderResponse:
    template = body.template if body.template in VALID_TEMPLATES else "classic"
    task = generate_pdf_task.delay(
        resume_id=str(resume_id),
        user_id=str(current_user.id),
        template=template,
    )
    return PDFRenderResponse(
        task_id=task.id,
        resume_id=str(resume_id),
        template=template,
    )


@router.get("/compare/{base_id}/{optimized_id}", response_model=ResumeComparisonResponse)
async def compare_versions(
    base_id: uuid.UUID,
    optimized_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ResumeComparisonResponse:
    uc = CompareResumeVersionsUseCase(PgResumeRepository(session))
    comparison = await uc.execute(
        base_id=base_id, optimized_id=optimized_id, user_id=current_user.id
    )
    return ResumeComparisonResponse(
        base_id=str(comparison.base.id),
        optimized_id=str(comparison.optimized.id),
        added_skills=comparison.added_skills,
        removed_skills=comparison.removed_skills,
        ats_score_delta=comparison.ats_score_delta,
        experience_delta=comparison.experience_delta,
    )


@router.post("/{resume_id}/rollback", response_model=ResumeResponse)
async def rollback_version(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ResumeResponse:
    uc = RollbackResumeVersionUseCase(PgResumeRepository(session))
    parent = await uc.execute(resume_id=resume_id, user_id=current_user.id)
    return _resume_response(parent)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    repo = PgResumeRepository(session)
    resume = await repo.get_by_id(resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    await repo.delete(resume_id)

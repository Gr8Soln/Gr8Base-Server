import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.ai.agents.jd_analyzer_agent import JDAnalyzerAgent
from app.adapters.api.dependencies.auth import get_current_user
from app.adapters.api.schemas.job_schemas import AnalyzeJobRequest, JobResponse, KeywordsResponse
from app.adapters.persistence.repositories.pg_job_repository import PgJobRepository
from app.adapters.queue.tasks.embedding_tasks import generate_job_embedding_task
from app.application.use_cases.jobs.analyze_job_description import (
    AnalyzeJobDescriptionUseCase,
    AnalyzeJobInput,
)
from app.application.use_cases.jobs.extract_keywords import ExtractKeywordsUseCase
from app.application.use_cases.jobs.get_job import GetJobUseCase
from app.domain.entities.job import JobDescription
from app.domain.entities.user import User
from app.infrastructure.database.connection import get_db_session

router = APIRouter()


def _job_response(job: JobDescription) -> JobResponse:
    return JobResponse(
        id=str(job.id),
        user_id=str(job.user_id),
        title=job.title,
        company=job.company,
        company_url=job.company_url,
        location=job.location,
        work_type=job.work_type,
        role=job.role,
        seniority=job.seniority,
        domain=job.domain,
        required_skills=job.required_skills,
        preferred_skills=job.preferred_skills,
        soft_skills=job.soft_skills,
        tools_and_technologies=job.tools_and_technologies,
        ats_keywords=job.ats_keywords,
        hidden_signals=job.hidden_signals,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
    )


@router.post("/analyze", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def analyze_job_description(
    body: AnalyzeJobRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> JobResponse:
    use_case = AnalyzeJobDescriptionUseCase(
        job_repo=PgJobRepository(session),
        analyzer=JDAnalyzerAgent(),
    )
    job = await use_case.execute(
        AnalyzeJobInput(
            user_id=current_user.id,
            raw_text=body.raw_text,
            company=body.company,
            company_url=body.company_url,
        )
    )

    # Dispatch async embedding generation
    generate_job_embedding_task.delay(
        job_id=str(job.id),
        raw_text=job.raw_text,
        required_skills=job.required_skills,
    )

    return _job_response(job)


@router.get("", response_model=list[JobResponse])
async def list_jobs(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[JobResponse]:
    repo = PgJobRepository(session)
    jobs = await repo.get_by_user_id(current_user.id)
    return [_job_response(j) for j in jobs]


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> JobResponse:
    use_case = GetJobUseCase(PgJobRepository(session))
    job = await use_case.execute(job_id=job_id, user_id=current_user.id)
    return _job_response(job)


@router.get("/{job_id}/keywords", response_model=KeywordsResponse)
async def get_job_keywords(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> KeywordsResponse:
    use_case = ExtractKeywordsUseCase(PgJobRepository(session))
    keywords = await use_case.execute(job_id=job_id, user_id=current_user.id)
    return KeywordsResponse(
        job_id=str(job_id),
        keywords=keywords,
        total=len(keywords),
    )


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    repo = PgJobRepository(session)
    job = await repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    if job.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    await repo.delete(job_id)

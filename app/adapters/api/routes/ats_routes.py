import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.api.dependencies.auth import get_current_user
from app.adapters.api.schemas.ats_schemas import (
    ATSScoreResponse,
    ScoreDimensionResponse,
    ScoreRequest,
    ScoreTaskResponse,
)
from app.adapters.persistence.repositories.pg_ats_repository import PgATSRepository
from app.adapters.queue.tasks.scoring_tasks import score_resume_task
from app.application.use_cases.ats.get_ats_score import GetATSScoreUseCase
from app.domain.entities.ats import ATSScore
from app.domain.entities.user import User
from app.infrastructure.database.connection import get_db_session

router = APIRouter()


def _ats_response(score: ATSScore) -> ATSScoreResponse:
    return ATSScoreResponse(
        id=str(score.id),
        resume_id=str(score.resume_id),
        job_id=str(score.job_id),
        overall_score=score.overall_score,
        dimensions=[
            ScoreDimensionResponse(
                name=d.name,
                score=d.score,
                weight=d.weight,
                feedback=d.feedback,
                suggestions=d.suggestions,
            )
            for d in score.dimensions
        ],
        missing_keywords=score.missing_keywords,
        weak_sections=score.weak_sections,
        recommendations=score.recommendations,
        recruiter_critique=score.recruiter_critique,
        is_ats_safe=score.is_ats_safe,
    )


@router.post("/score", response_model=ScoreTaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_ats_score(
    body: ScoreRequest,
    current_user: User = Depends(get_current_user),
) -> ScoreTaskResponse:
    task = score_resume_task.delay(
        resume_id=body.resume_id,
        job_id=body.job_id,
        user_id=str(current_user.id),
    )
    return ScoreTaskResponse(
        task_id=task.id,
        resume_id=body.resume_id,
        job_id=body.job_id,
    )


@router.get("/scores/{score_id}", response_model=ATSScoreResponse)
async def get_ats_score(
    score_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ATSScoreResponse:
    use_case = GetATSScoreUseCase(PgATSRepository(session))
    score = await use_case.execute(score_id=score_id, user_id=current_user.id)
    return _ats_response(score)


@router.get("/scores", response_model=list[ATSScoreResponse])
async def list_ats_scores(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[ATSScoreResponse]:
    repo = PgATSRepository(session)
    scores = await repo.get_by_user_id(current_user.id)
    return [_ats_response(s) for s in scores]

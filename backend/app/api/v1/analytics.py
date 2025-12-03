from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_active_user
from app.db import get_session
from app.models import Survey
from app.schemas import QuestionAnalytics, SurveyAnalytics, UserRead
from app.services.analytics import get_question_analytics, get_survey_analytics


router = APIRouter()


@router.get("/{survey_id}/analytics", response_model=SurveyAnalytics)
async def survey_analytics(
    survey_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_active_user),
):
    survey = await session.get(Survey, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    if survey.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await get_survey_analytics(session, survey_id)


@router.get("/{survey_id}/analytics/question/{question_id}", response_model=QuestionAnalytics)
async def question_analytics(
    survey_id: UUID,
    question_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_active_user),
):
    survey = await session.get(Survey, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    if survey.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await get_question_analytics(session, survey_id, question_id)



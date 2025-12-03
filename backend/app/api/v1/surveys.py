from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_active_user, get_current_user_optional
from app.crud import (
    add_option_to_question,
    add_question_to_survey,
    create_survey_with_questions,
    delete_question,
    delete_survey,
    list_surveys,
    update_question,
    update_survey,
)
from app.db import get_session
from app.models import Question, Survey
from app.schemas import (
    OptionCreate,
    QuestionCreate,
    QuestionRead,
    QuestionUpdate,
    SurveyCreate,
    SurveyRead,
    SurveyUpdate,
    UserRead,
)


router = APIRouter()


@router.get("", response_model=List[SurveyRead])
async def get_surveys(
    owner_id: Optional[UUID] = Query(default=None),
    published: Optional[bool] = Query(default=None),
    session: AsyncSession = Depends(get_session),
    current_user: Optional[UserRead] = Depends(get_current_user_optional),
):
    if owner_id is None and current_user is None and published is None:
        published = True

    surveys = await list_surveys(
        session=session,
        owner_id=owner_id,
        published=published,
    )
    return [SurveyRead.model_validate(s) for s in surveys]


@router.post("", response_model=SurveyRead, status_code=status.HTTP_201_CREATED)
async def create_survey(
    survey_in: SurveyCreate,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_active_user),
):
    survey = await create_survey_with_questions(session, current_user.id, survey_in)
    return SurveyRead.model_validate(survey)


@router.get("/{survey_id}", response_model=SurveyRead)
async def get_survey_detail(
    survey_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: Optional[UserRead] = Depends(get_current_user_optional),
):
    survey: Survey | None = await session.get(Survey, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    await session.refresh(survey, attribute_names=["questions"])
    for q in survey.questions:
        await session.refresh(q, attribute_names=["options"])
    return SurveyRead.model_validate(survey)


@router.put("/{survey_id}", response_model=SurveyRead)
async def update_survey_endpoint(
    survey_id: UUID,
    survey_in: SurveyUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_active_user),
):
    survey: Survey | None = await session.get(Survey, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    if survey.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    survey = await update_survey(session, survey, survey_in)
    return SurveyRead.model_validate(survey)


@router.delete("/{survey_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_survey_endpoint(
    survey_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_active_user),
):
    survey: Survey | None = await session.get(Survey, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    if survey.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    await delete_survey(session, survey)
    return


@router.post("/{survey_id}/publish", response_model=SurveyRead)
async def toggle_publish(
    survey_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_active_user),
):
    survey: Survey | None = await session.get(Survey, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    if survey.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    survey.is_published = not survey.is_published
    session.add(survey)
    await session.commit()
    result = await session.execute(
        select(Survey)
        .where(Survey.id == survey_id)
        .options(
            selectinload(Survey.questions).selectinload(Question.options)
        )
    )
    survey = result.scalar_one()
    return SurveyRead.model_validate(survey)


@router.post("/{survey_id}/questions", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
async def add_question(
    survey_id: UUID,
    q_in: QuestionCreate,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_active_user),
):
    survey: Survey | None = await session.get(Survey, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    if survey.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    question = await add_question_to_survey(session, survey_id, q_in)
    return QuestionRead.model_validate(question)


@router.put("/questions/{question_id}", response_model=QuestionRead)
async def update_question_endpoint(
    question_id: UUID,
    q_in: QuestionUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_active_user),
):
    question: Question | None = await session.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    survey: Survey | None = await session.get(Survey, question.survey_id)
    if not survey or survey.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    question = await update_question(session, question, q_in)
    return QuestionRead.model_validate(question)


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question_endpoint(
    question_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_active_user),
):
    question: Question | None = await session.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    survey: Survey | None = await session.get(Survey, question.survey_id)
    if not survey or survey.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    await delete_question(session, question)
    return


@router.post("/questions/{question_id}/options", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
async def add_option(
    question_id: UUID,
    opt_in: OptionCreate,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_active_user),
):
    question: Question | None = await session.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    survey: Survey | None = await session.get(Survey, question.survey_id)
    if not survey or survey.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    await add_option_to_question(session, question_id, opt_in.text, opt_in.order)
    await session.refresh(question, attribute_names=["options"])
    return QuestionRead.model_validate(question)



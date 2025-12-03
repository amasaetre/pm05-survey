from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import AnswerOption, AnswerValue, Option, Question, Response, Survey, User
from app.schemas import (
    AnswerValueSubmit,
    QuestionCreate,
    QuestionUpdate,
    SurveyCreate,
    SurveyUpdate,
)


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def create_user(session: AsyncSession, user: User) -> User:
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_user(session: AsyncSession, user_id: UUID) -> Optional[User]:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def create_survey_with_questions(
    session: AsyncSession,
    owner_id: UUID,
    survey_in: SurveyCreate,
) -> Survey:
    survey = Survey(
        title=survey_in.title,
        description=survey_in.description,
        owner_id=owner_id,
        settings=survey_in.settings,
    )
    session.add(survey)
    await session.flush()

    if survey_in.questions:
        for idx, q in enumerate(survey_in.questions):
            question = Question(
                survey_id=survey.id,
                text=q.text,
                type=q.type,
                required=q.required,
                order=q.order if q.order is not None else idx,
                meta=q.meta,
            )
            session.add(question)
            await session.flush()
            if q.options:
                for o_idx, opt in enumerate(q.options):
                    option = Option(
                        question_id=question.id,
                        text=opt.text,
                        order=opt.order if opt.order is not None else o_idx,
                    )
                    session.add(option)

    await session.commit()
    result = await session.execute(
        select(Survey)
        .where(Survey.id == survey.id)
        .options(
            selectinload(Survey.questions).selectinload(Question.options)
        )
    )
    survey = result.scalar_one()
    return survey


async def list_surveys(
    session: AsyncSession,
    owner_id: Optional[UUID] = None,
    published: Optional[bool] = None,
) -> List[Survey]:
    stmt = select(Survey).options(
        selectinload(Survey.questions).selectinload(Question.options)
    )
    if owner_id is not None:
        stmt = stmt.where(Survey.owner_id == owner_id)
    if published is not None:
        stmt = stmt.where(Survey.is_published == published)
    result = await session.execute(stmt.order_by(Survey.created_at.desc()))
    return list(result.scalars().unique())


async def get_survey_with_questions(session: AsyncSession, survey_id: UUID) -> Optional[Survey]:
    result = await session.execute(
        select(Survey)
        .where(Survey.id == survey_id)
        .options(
            selectinload(Survey.questions).selectinload(Question.options)
        )
    )
    return result.scalars().first()


async def update_survey(
    session: AsyncSession,
    survey: Survey,
    survey_in: SurveyUpdate,
) -> Survey:
    data = survey_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(survey, field, value)
    session.add(survey)
    await session.commit()
    result = await session.execute(
        select(Survey)
        .where(Survey.id == survey.id)
        .options(
            selectinload(Survey.questions).selectinload(Question.options)
        )
    )
    survey = result.scalar_one()
    return survey


async def delete_survey(session: AsyncSession, survey: Survey) -> None:
    await session.delete(survey)
    await session.commit()


async def add_question_to_survey(
    session: AsyncSession,
    survey_id: UUID,
    q_in: QuestionCreate,
) -> Question:
    question = Question(
        survey_id=survey_id,
        text=q_in.text,
        type=q_in.type,
        required=q_in.required,
        order=q_in.order,
        meta=q_in.meta,
    )
    session.add(question)
    await session.flush()
    if q_in.options:
        for o_idx, opt in enumerate(q_in.options):
            option = Option(
                question_id=question.id,
                text=opt.text,
                order=opt.order if opt.order is not None else o_idx,
            )
            session.add(option)
    await session.commit()
    await session.refresh(question)
    return question


async def update_question(
    session: AsyncSession,
    question: Question,
    q_in: QuestionUpdate,
) -> Question:
    data = q_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(question, field, value)
    session.add(question)
    await session.commit()
    await session.refresh(question)
    return question


async def delete_question(session: AsyncSession, question: Question) -> None:
    await session.delete(question)
    await session.commit()


async def add_option_to_question(
    session: AsyncSession,
    question_id: UUID,
    text: str,
    order: int = 0,
) -> Option:
    option = Option(question_id=question_id, text=text, order=order)
    session.add(option)
    await session.commit()
    await session.refresh(option)
    return option


async def submit_response(
    session: AsyncSession,
    survey_id: UUID,
    user_id: Optional[UUID],
    answers: List[AnswerValueSubmit],
    meta: Optional[dict] = None,
    session_id: Optional[str] = None,
) -> Response:
    response = Response(
        survey_id=survey_id,
        user_id=user_id,
        session_id=session_id,
        meta=meta
    )
    session.add(response)
    await session.flush()

    for answer in answers:
        av = AnswerValue(
            response_id=response.id,
            question_id=answer.question_id,
            value_text=answer.value_text,
            value_number=answer.value_number,
        )
        session.add(av)
        await session.flush()
        if answer.option_ids:
            for opt_id in answer.option_ids:
                session.add(
                    AnswerOption(
                        answer_value_id=av.id,
                        option_id=opt_id,
                    )
                )

    await session.commit()
    await session.refresh(response)
    return response


